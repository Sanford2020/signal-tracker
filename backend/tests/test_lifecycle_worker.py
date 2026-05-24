from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import AlertEvent, IntelFile, RawItem
from app.models.enums import AlertType, LifecycleStatus


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_file(client: TestClient, title: str = "Example AI hiring hardware role") -> str:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": title,
            "content": "Example AI is hiring hardware supply chain operators.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def _create_raw_item(client: TestClient, db_session: Session, captured_at: datetime) -> str:
    follow_up = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Example AI posts official hardware role",
            "content": "A fresh official careers update confirms hardware hiring.",
        },
    )
    assert follow_up.status_code == 200
    raw_item_id = follow_up.json()["data"]["raw_item"]["id"]
    raw_item = db_session.get(RawItem, UUID(raw_item_id))
    assert raw_item is not None
    raw_item.captured_at = captured_at
    db_session.commit()
    return raw_item_id


def test_lifecycle_worker_marks_stale_files_dormant(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id = _create_file(client)
    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.status = LifecycleStatus.WATCHING
    intel_file.last_seen_at = datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC)
    db_session.commit()

    response = client.post(
        "/api/v1/lifecycle/run",
        json={"now": "2026-05-23T12:00:00+00:00", "reason": "worker test"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checked_count"] == 1
    assert data["transitioned_count"] == 1
    assert data["items"][0]["next_status"] == "dormant"
    db_session.refresh(intel_file)
    assert intel_file.status == LifecycleStatus.DORMANT


def test_lifecycle_worker_resurrects_dormant_files_with_recent_evidence(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id = _create_file(client)
    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.status = LifecycleStatus.DORMANT
    intel_file.last_seen_at = datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC)
    db_session.commit()

    raw_item_id = _create_raw_item(
        client,
        db_session,
        captured_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
    )
    attach = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={
            "raw_item_id": raw_item_id,
            "evidence_type": "follow_up",
            "confidence": 0.9,
            "rationale": "Meaningful recent follow-up.",
        },
    )
    assert attach.status_code == 200

    response = client.post(
        "/api/v1/lifecycle/run",
        json={"now": "2026-05-23T12:00:00+00:00", "reason": "worker test"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checked_count"] == 1
    assert data["transitioned_count"] == 1
    assert data["items"][0]["previous_status"] == "dormant"
    assert data["items"][0]["next_status"] == "resurrected"
    db_session.refresh(intel_file)
    assert intel_file.status == LifecycleStatus.RESURRECTED

    alert = db_session.scalar(
        select(AlertEvent).where(
            AlertEvent.intel_file_id == UUID(intel_file_id),
            AlertEvent.alert_type == AlertType.RESURRECTED,
        )
    )
    assert alert is not None


def test_lifecycle_worker_respects_limit(client: TestClient, db_session: Session) -> None:
    first_id = _create_file(client, "First stale signal")
    second_id = _create_file(client, "Second stale signal")
    for intel_file_id in [first_id, second_id]:
        intel_file = db_session.get(IntelFile, UUID(intel_file_id))
        assert intel_file is not None
        intel_file.status = LifecycleStatus.WATCHING
        intel_file.last_seen_at = datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC)
    db_session.commit()

    response = client.post(
        "/api/v1/lifecycle/run",
        json={"now": "2026-05-23T12:00:00+00:00", "limit": 1},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checked_count"] == 1
    assert data["transitioned_count"] == 1


def test_lifecycle_worker_noops_when_no_candidates(client: TestClient) -> None:
    _create_file(client)

    response = client.post(
        "/api/v1/lifecycle/run",
        json={"now": "2026-05-23T12:00:00+00:00"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "checked_count": 0,
        "transitioned_count": 0,
        "items": [],
    }
