from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import AlertEvent, NotificationDeliveryAttempt
from app.models.enums import AlertSeverity, AlertStatus, AlertType


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
        json={"email": "notify@example.com", "name": "Notify", "workspace_name": "Notify Workspace"},
    )
    assert response.status_code == 200
    return response.json()["data"]["workspace"]["id"]


def _create_file(client: TestClient, workspace_id: str) -> str:
    submit = client.post(
        "/api/v1/inbox/submit",
        headers={"X-Workspace-Id": workspace_id},
        json={"title": "Notification signal", "content": "Notification signal content."},
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def _create_alert(db_session: Session, intel_file_id: str) -> AlertEvent:
    alert = AlertEvent(
        intel_file_id=UUID(intel_file_id),
        alert_type=AlertType.RESURRECTED,
        severity=AlertSeverity.IMPORTANT,
        message="test|Signal resurrected.",
        status=AlertStatus.PENDING,
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert


def test_create_and_list_notification_channels(client: TestClient) -> None:
    workspace_id = _bootstrap(client)
    headers = {"X-Workspace-Id": workspace_id}

    response = client.post(
        "/api/v1/notifications/channels",
        headers=headers,
        json={"name": "Ops Email", "channel": "email", "target": "ops@example.com"},
    )

    assert response.status_code == 200
    item = response.json()["data"]["item"]
    assert item["workspace_id"] == workspace_id
    assert item["channel"] == "email"

    listed = client.get("/api/v1/notifications/channels", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["data"]["total"] == 1


def test_delivery_run_sends_pending_alerts(
    client: TestClient,
    db_session: Session,
) -> None:
    workspace_id = _bootstrap(client)
    file_id = _create_file(client, workspace_id)
    alert = _create_alert(db_session, file_id)
    headers = {"X-Workspace-Id": workspace_id}
    client.post(
        "/api/v1/notifications/channels",
        headers=headers,
        json={"name": "Webhook", "channel": "webhook", "target": "https://example.com/hook"},
    )

    response = client.post("/api/v1/notifications/deliveries/run", headers=headers, json={"limit": 10})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checked_alert_count"] == 1
    assert data["delivered_count"] == 1
    assert data["attempts"][0]["alert_event_id"] == str(alert.id)

    db_session.refresh(alert)
    assert alert.status == AlertStatus.SENT
    assert len(db_session.scalars(select(NotificationDeliveryAttempt)).all()) == 1


def test_delivery_run_is_idempotent_for_sent_alerts(
    client: TestClient,
    db_session: Session,
) -> None:
    workspace_id = _bootstrap(client)
    file_id = _create_file(client, workspace_id)
    _create_alert(db_session, file_id)
    headers = {"X-Workspace-Id": workspace_id}
    client.post(
        "/api/v1/notifications/channels",
        headers=headers,
        json={"name": "Webhook", "channel": "webhook", "target": "https://example.com/hook"},
    )

    first = client.post("/api/v1/notifications/deliveries/run", headers=headers, json={})
    second = client.post("/api/v1/notifications/deliveries/run", headers=headers, json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["delivered_count"] == 1
    assert second.json()["data"]["delivered_count"] == 0
