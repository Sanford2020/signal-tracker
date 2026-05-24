from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import clear_rate_limit_state
from app.db.session import get_db
from app.main import app


def test_bootstrap_requires_admin_secret_in_production(monkeypatch, db_session: Session) -> None:
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

    response = client.post(
        "/api/v1/auth/bootstrap",
        json={"email": "owner@example.com", "name": "Owner", "workspace_name": "Owner Workspace"},
    )

    assert response.status_code == 401

    allowed = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Admin-Secret": "expected-secret"},
        json={"email": "owner@example.com", "name": "Owner", "workspace_name": "Owner Workspace"},
    )

    assert allowed.status_code == 200

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    clear_rate_limit_state()


def test_bootstrap_is_rate_limited_in_production(monkeypatch, db_session: Session) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://prod_user:prod_pass@db.example.com:5432/signal_tracker",
    )
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("ADMIN_API_KEY", "expected-secret")
    monkeypatch.setenv("ADMIN_RATE_LIMIT_PER_MINUTE", "1")
    get_settings.cache_clear()
    clear_rate_limit_state()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, raise_server_exceptions=True)

    first = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Admin-Secret": "expected-secret"},
        json={"email": "owner@example.com", "name": "Owner", "workspace_name": "Owner Workspace"},
    )
    second = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Admin-Secret": "expected-secret"},
        json={"email": "other@example.com", "name": "Other", "workspace_name": "Other Workspace"},
    )

    assert first.status_code == 200
    assert second.status_code == 429

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    clear_rate_limit_state()
