import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.main import app


@pytest.fixture
def production_client(monkeypatch, db_session: Session) -> TestClient:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://prod_user:prod_pass@db.example.com:5432/signal_tracker",
    )
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("ADMIN_API_KEY", "expected-secret")
    get_settings.cache_clear()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, raise_server_exceptions=True)
    yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _bootstrap(client: TestClient, email: str, workspace_name: str) -> tuple[str, str]:
    response = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Admin-Secret": "expected-secret"},
        json={"email": email, "name": email.split("@")[0], "workspace_name": workspace_name},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    return data["workspace"]["id"], data["access_token"]


def test_workspace_routes_require_user_email_in_production(production_client: TestClient) -> None:
    workspace_id, _ = _bootstrap(production_client, "alice@example.com", "Alice Workspace")

    response = production_client.get(
        "/api/v1/intel-files",
        headers={"X-Workspace-Id": workspace_id},
    )

    assert response.status_code == 401


def test_workspace_routes_reject_non_members_in_production(production_client: TestClient) -> None:
    workspace_id, _ = _bootstrap(production_client, "alice@example.com", "Alice Workspace")

    response = production_client.get(
        "/api/v1/intel-files",
        headers={"X-Workspace-Id": workspace_id, "X-User-Email": "mallory@example.com", "X-User-Token": "bogus"},
    )

    assert response.status_code == 403


def test_workspace_routes_allow_members_in_production(production_client: TestClient) -> None:
    workspace_id, access_token = _bootstrap(production_client, "alice@example.com", "Alice Workspace")

    response = production_client.get(
        "/api/v1/intel-files",
        headers={"X-Workspace-Id": workspace_id, "X-User-Email": "alice@example.com", "X-User-Token": access_token},
    )

    assert response.status_code == 200


def test_workspace_routes_reject_missing_user_token_in_production(production_client: TestClient) -> None:
    workspace_id, _ = _bootstrap(production_client, "alice@example.com", "Alice Workspace")

    response = production_client.get(
        "/api/v1/intel-files",
        headers={"X-Workspace-Id": workspace_id, "X-User-Email": "alice@example.com"},
    )

    assert response.status_code == 401
