import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _bootstrap(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={"email": "usage@example.com", "name": "Usage", "workspace_name": "Usage Workspace"},
    )
    assert response.status_code == 200
    return response.json()["data"]["workspace"]["id"]


def _submit_raw(client: TestClient, workspace_id: str, title: str) -> str:
    response = client.post(
        "/api/v1/inbox/submit",
        headers={"X-Workspace-Id": workspace_id},
        json={"title": title, "content": f"{title} content."},
    )
    assert response.status_code == 200
    return response.json()["data"]["raw_item"]["id"]


def _create_file_with_queries(client: TestClient, workspace_id: str) -> None:
    raw_item_id = _submit_raw(client, workspace_id, "Usage source check signal")
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    file_id = create_file.json()["data"]["intel_file"]["id"]
    assert client.post(f"/api/v1/intel-files/{file_id}/tracking-queries", json={"limit": 2}).status_code == 200


def test_usage_summary_records_ai_extraction(client: TestClient) -> None:
    workspace_id = _bootstrap(client)
    raw_item_id = _submit_raw(client, workspace_id, "Usage AI signal")

    response = client.post(f"/api/v1/raw-items/{raw_item_id}/analyze")

    assert response.status_code == 200
    summary = client.get("/api/v1/usage/summary", headers={"X-Workspace-Id": workspace_id})
    assert summary.status_code == 200
    assert summary.json()["data"]["totals"]["ai_extraction"] == 1


def test_ai_extraction_limit_returns_429(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USAGE_AI_EXTRACTION_MONTHLY_LIMIT", "0")
    from app.core.config import get_settings

    get_settings.cache_clear()
    workspace_id = _bootstrap(client)
    raw_item_id = _submit_raw(client, workspace_id, "Usage AI limited signal")

    response = client.post(f"/api/v1/raw-items/{raw_item_id}/analyze")

    assert response.status_code == 429


def test_source_check_usage_records_checked_queries(client: TestClient) -> None:
    workspace_id = _bootstrap(client)
    _create_file_with_queries(client, workspace_id)

    response = client.post(
        "/api/v1/source-checks/run",
        headers={"X-Workspace-Id": workspace_id},
        json={"limit": 2},
    )

    assert response.status_code == 200
    summary = client.get("/api/v1/usage/summary", headers={"X-Workspace-Id": workspace_id})
    assert summary.status_code == 200
    assert summary.json()["data"]["totals"]["source_check"] == 2


def test_source_check_limit_returns_429(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USAGE_SOURCE_CHECK_MONTHLY_LIMIT", "0")
    from app.core.config import get_settings

    get_settings.cache_clear()
    workspace_id = _bootstrap(client)
    _create_file_with_queries(client, workspace_id)

    response = client.post(
        "/api/v1/source-checks/run",
        headers={"X-Workspace-Id": workspace_id},
        json={"limit": 2},
    )

    assert response.status_code == 429
