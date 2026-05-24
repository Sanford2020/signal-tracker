from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import AlertEvent, IntelEvent, IntelFile, LifecycleSnapshot
from app.models.enums import AlertType, IntelEventType, LifecycleStatus


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_file(client: TestClient) -> str:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Example AI policy signal",
            "content": "Example AI appears in a policy consultation draft.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def test_status_override_updates_file_and_logs_event(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id = _create_file(client)

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/status",
        json={
            "status": "verified",
            "reason": "Official source confirmed the signal.",
            "now": "2026-05-23T12:00:00+00:00",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["previous_status"] == "new"
    assert data["next_status"] == "verified"

    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    assert intel_file.status == LifecycleStatus.VERIFIED

    event = db_session.scalar(
        select(IntelEvent).where(
            IntelEvent.intel_file_id == UUID(intel_file_id),
            IntelEvent.event_type == IntelEventType.STATUS_CHANGED,
        )
    )
    assert event is not None
    assert event.title == "Status manually changed to verified"
    assert event.description == "Official source confirmed the signal."

    snapshot = db_session.scalar(
        select(LifecycleSnapshot).where(LifecycleSnapshot.intel_file_id == UUID(intel_file_id))
    )
    assert snapshot is not None
    assert snapshot.status == LifecycleStatus.VERIFIED
    assert snapshot.snapshot_time.replace(tzinfo=UTC) == datetime(2026, 5, 23, 12, 0, 0, tzinfo=UTC)


def test_status_override_triggers_resurrection_alert(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id = _create_file(client)
    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.status = LifecycleStatus.DORMANT
    db_session.commit()

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/status",
        json={"status": "resurrected", "reason": "Analyst confirmed renewed activity."},
    )

    assert response.status_code == 200
    alert = db_session.scalar(
        select(AlertEvent).where(
            AlertEvent.intel_file_id == UUID(intel_file_id),
            AlertEvent.alert_type == AlertType.RESURRECTED,
        )
    )
    assert alert is not None


def test_status_override_requires_reason(client: TestClient) -> None:
    intel_file_id = _create_file(client)

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/status",
        json={"status": "noise", "reason": ""},
    )

    assert response.status_code == 422


def test_status_override_missing_file_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/intel-files/00000000-0000-0000-0000-000000000001/status",
        json={"status": "noise", "reason": "No reliable source."},
    )

    assert response.status_code == 404
