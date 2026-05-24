from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.main import app
from app.models import AlertEvent, IntelFile, SourceCheckRun
from app.models.enums import AlertSeverity, AlertStatus, AlertType, LifecycleStatus


@pytest.fixture
def production_client(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> TestClient:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://prod_user:prod_pass@db.example.com:5432/signal_tracker",
    )
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-secret")
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
        headers={"X-Admin-Secret": "test-admin-secret"},
        json={"email": email, "name": email.split("@")[0], "workspace_name": workspace_name},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    return data["workspace"]["id"], data["access_token"]


def _auth_headers(workspace_id: str, email: str, token: str) -> dict[str, str]:
    return {
        "X-Workspace-Id": workspace_id,
        "X-User-Email": email,
        "X-User-Token": token,
    }


def _create_file(
    db_session: Session,
    *,
    workspace_id: str,
    title: str,
) -> IntelFile:
    intel_file = IntelFile(
        workspace_id=UUID(workspace_id),
        title=title,
        thesis=f"{title} thesis",
        status=LifecycleStatus.NEW,
        first_seen_at=datetime(2026, 5, 24, 8, 0, tzinfo=UTC),
        last_seen_at=datetime(2026, 5, 24, 8, 0, tzinfo=UTC),
        keywords=["ai"],
        entities=[],
        evidence_count=0,
        source_count=1,
        heat_score=5.0,
        credibility_score=5.0,
        opportunity_score=8.0,
        risk_score=2.0,
    )
    db_session.add(intel_file)
    db_session.commit()
    db_session.refresh(intel_file)
    return intel_file


def test_briefings_and_reports_are_workspace_scoped(
    production_client: TestClient,
    db_session: Session,
) -> None:
    first_workspace, first_token = _bootstrap(production_client, "first@example.com", "First Workspace")
    second_workspace, _ = _bootstrap(production_client, "second@example.com", "Second Workspace")
    _create_file(db_session, workspace_id=first_workspace, title="First private signal")
    _create_file(db_session, workspace_id=second_workspace, title="Second private signal")

    headers = _auth_headers(first_workspace, "first@example.com", first_token)
    briefing = production_client.get("/api/v1/briefings/daily?hours=168", headers=headers)
    assert briefing.status_code == 200
    rendered = str(briefing.json()["data"])
    assert "First private signal" in rendered
    assert "Second private signal" not in rendered

    report = production_client.get("/api/v1/reports/daily.md?hours=168", headers=headers)
    assert report.status_code == 200
    assert "First private signal" in report.text
    assert "Second private signal" not in report.text


def test_alerts_are_workspace_scoped(
    production_client: TestClient,
    db_session: Session,
) -> None:
    first_workspace, first_token = _bootstrap(production_client, "alerts-a@example.com", "Alerts A")
    second_workspace, _ = _bootstrap(production_client, "alerts-b@example.com", "Alerts B")
    first_file = _create_file(db_session, workspace_id=first_workspace, title="First alert signal")
    second_file = _create_file(db_session, workspace_id=second_workspace, title="Second alert signal")
    db_session.add_all(
        [
            AlertEvent(
                intel_file_id=first_file.id,
                alert_type=AlertType.OPPORTUNITY_UP,
                severity=AlertSeverity.IMPORTANT,
                message="first|First workspace alert",
                status=AlertStatus.PENDING,
            ),
            AlertEvent(
                intel_file_id=second_file.id,
                alert_type=AlertType.OPPORTUNITY_UP,
                severity=AlertSeverity.IMPORTANT,
                message="second|Second workspace alert",
                status=AlertStatus.PENDING,
            ),
        ]
    )
    db_session.commit()

    headers = _auth_headers(first_workspace, "alerts-a@example.com", first_token)
    response = production_client.get("/api/v1/alerts", headers=headers)
    assert response.status_code == 200
    titles = {item["intel_file_title"] for item in response.json()["data"]["items"]}
    assert titles == {"First alert signal"}


def test_source_check_runs_are_workspace_scoped(
    production_client: TestClient,
    db_session: Session,
) -> None:
    first_workspace, first_token = _bootstrap(production_client, "runs-a@example.com", "Runs A")
    second_workspace, _ = _bootstrap(production_client, "runs-b@example.com", "Runs B")
    db_session.add_all(
        [
            SourceCheckRun(workspace_id=UUID(first_workspace), status="completed", checked_query_count=1, result_count=1),
            SourceCheckRun(workspace_id=UUID(second_workspace), status="completed", checked_query_count=1, result_count=1),
            SourceCheckRun(workspace_id=None, status="completed", checked_query_count=1, result_count=1),
        ]
    )
    db_session.commit()

    headers = _auth_headers(first_workspace, "runs-a@example.com", first_token)
    response = production_client.get("/api/v1/source-checks/runs", headers=headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["workspace_id"] == first_workspace


def test_workspace_scoped_routes_reject_missing_credentials(production_client: TestClient) -> None:
    workspace_id, _ = _bootstrap(production_client, "guard@example.com", "Guard Workspace")
    response = production_client.get("/api/v1/briefings/daily", headers={"X-Workspace-Id": workspace_id})
    assert response.status_code == 401
