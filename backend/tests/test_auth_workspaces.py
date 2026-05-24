from uuid import UUID

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


def _bootstrap(client: TestClient, email: str, workspace_name: str) -> str:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={"email": email, "name": email.split("@")[0], "workspace_name": workspace_name},
    )
    assert response.status_code == 200
    return response.json()["data"]["workspace"]["id"]


def _create_file_in_workspace(client: TestClient, workspace_id: str, title: str) -> str:
    headers = {"X-Workspace-Id": workspace_id}
    submit = client.post(
        "/api/v1/inbox/submit",
        headers=headers,
        json={"title": title, "content": f"{title} workspace scoped content."},
    )
    assert submit.status_code == 200
    raw_item = submit.json()["data"]["raw_item"]
    assert raw_item["workspace_id"] == workspace_id

    analyze = client.post(f"/api/v1/raw-items/{raw_item['id']}/analyze")
    assert analyze.status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item["id"]})
    assert create_file.status_code == 200
    file = create_file.json()["data"]["intel_file"]
    assert file["workspace_id"] == workspace_id
    return file["id"]


def test_bootstrap_creates_user_workspace_and_membership(client: TestClient) -> None:
    workspace_id = _bootstrap(client, "alice@example.com", "Alice Workspace")

    response = client.get("/api/v1/workspaces", headers={"X-User-Email": "alice@example.com"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["id"] == workspace_id
    assert data["items"][0]["slug"] == "alice-workspace"


def test_workspace_scoped_intel_file_listing(client: TestClient) -> None:
    first_workspace = _bootstrap(client, "first@example.com", "First Team")
    second_workspace = _bootstrap(client, "second@example.com", "Second Team")
    first_file = _create_file_in_workspace(client, first_workspace, "First team signal")
    second_file = _create_file_in_workspace(client, second_workspace, "Second team signal")

    first_list = client.get("/api/v1/intel-files", headers={"X-Workspace-Id": first_workspace})
    second_list = client.get("/api/v1/intel-files", headers={"X-Workspace-Id": second_workspace})

    assert first_list.status_code == 200
    assert second_list.status_code == 200
    assert [item["id"] for item in first_list.json()["data"]["items"]] == [first_file]
    assert [item["id"] for item in second_list.json()["data"]["items"]] == [second_file]

    hidden = client.get(f"/api/v1/intel-files/{second_file}", headers={"X-Workspace-Id": first_workspace})
    assert hidden.status_code == 404


def test_unknown_workspace_header_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/v1/intel-files",
        headers={"X-Workspace-Id": str(UUID("00000000-0000-0000-0000-000000000001"))},
    )

    assert response.status_code == 404
