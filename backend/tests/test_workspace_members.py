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


def test_admin_can_add_and_list_workspace_members(production_client: TestClient) -> None:
    workspace_id, alice_token = _bootstrap(production_client, "alice@example.com", "Alice Workspace")

    added = production_client.post(
        f"/api/v1/workspaces/{workspace_id}/members",
        headers={"X-User-Email": "alice@example.com", "X-User-Token": alice_token},
        json={"email": "bob@example.com", "name": "Bob", "role": "member"},
    )

    assert added.status_code == 200
    bob_token = added.json()["data"]["access_token"]
    assert added.json()["data"]["member"]["email"] == "bob@example.com"

    listed = production_client.get(
        f"/api/v1/workspaces/{workspace_id}/members",
        headers={"X-User-Email": "bob@example.com", "X-User-Token": bob_token},
    )

    assert listed.status_code == 200
    emails = [item["email"] for item in listed.json()["data"]["items"]]
    assert emails == ["alice@example.com", "bob@example.com"]

    audit = production_client.get(
        f"/api/v1/workspaces/{workspace_id}/audit-events",
        headers={"X-User-Email": "alice@example.com", "X-User-Token": alice_token},
    )
    assert audit.status_code == 200
    actions = [item["action"] for item in audit.json()["data"]["items"]]
    assert set(actions) == {"workspace.bootstrap", "workspace.member.upsert"}

    exported = production_client.get(
        f"/api/v1/workspaces/{workspace_id}/audit-events.csv",
        headers={"X-User-Email": "alice@example.com", "X-User-Token": alice_token},
    )
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    assert "workspace.bootstrap" in exported.text
    assert "workspace.member.upsert" in exported.text


def test_member_cannot_add_workspace_members(production_client: TestClient) -> None:
    workspace_id, alice_token = _bootstrap(production_client, "alice@example.com", "Alice Workspace")
    added = production_client.post(
        f"/api/v1/workspaces/{workspace_id}/members",
        headers={"X-User-Email": "alice@example.com", "X-User-Token": alice_token},
        json={"email": "bob@example.com", "name": "Bob", "role": "member"},
    )
    assert added.status_code == 200
    bob_token = added.json()["data"]["access_token"]

    denied = production_client.post(
        f"/api/v1/workspaces/{workspace_id}/members",
        headers={"X-User-Email": "bob@example.com", "X-User-Token": bob_token},
        json={"email": "carol@example.com", "name": "Carol", "role": "member"},
    )

    assert denied.status_code == 403
