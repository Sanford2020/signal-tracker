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


def test_full_mvp_lifecycle_loop(client: TestClient, db_session: Session) -> None:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Example AI hiring hardware supply chain lead",
            "content": "Example AI is hiring a hardware supply chain lead.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]

    analyze = client.post(f"/api/v1/raw-items/{raw_item_id}/analyze")
    assert analyze.status_code == 200
    assert analyze.json()["data"]["analysis"]["signal_type"] == "hiring"

    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    intel_file_id = create_file.json()["data"]["intel_file"]["id"]

    score = client.post(f"/api/v1/intel-files/{intel_file_id}/score", json={"reason": "acceptance"})
    assert score.status_code == 200
    assert score.json()["data"]["opportunity_score"] is not None

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.DORMANT
    stored.last_seen_at = datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC)
    db_session.commit()

    follow_up = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Example AI posts official hardware supply chain role",
            "content": "A fresh official careers update confirms hardware hiring.",
        },
    )
    assert follow_up.status_code == 200
    follow_up_id = follow_up.json()["data"]["raw_item"]["id"]
    follow_up_item = db_session.get(RawItem, UUID(follow_up_id))
    assert follow_up_item is not None
    follow_up_item.captured_at = datetime(2026, 5, 25, 12, 0, 0, tzinfo=UTC)
    db_session.commit()

    attach = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={
            "raw_item_id": follow_up_id,
            "evidence_type": "follow_up",
            "confidence": 0.9,
            "rationale": "New meaningful primary-source follow-up after dormancy.",
        },
    )
    assert attach.status_code == 200

    evaluate = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evaluate",
        json={"reason": "acceptance", "now": "2026-05-26T12:00:00+00:00"},
    )
    assert evaluate.status_code == 200
    transition = evaluate.json()["data"]
    assert transition["previous_status"] == "dormant"
    assert transition["next_status"] == "resurrected"

    alert = db_session.scalar(
        select(AlertEvent).where(
            AlertEvent.intel_file_id == UUID(intel_file_id),
            AlertEvent.alert_type == AlertType.RESURRECTED,
        )
    )
    assert alert is not None

    briefing = client.get("/api/v1/briefings/daily?hours=168")
    assert briefing.status_code == 200
    resurrected = briefing.json()["data"]["sections"]["resurrected"]
    assert any(item["intel_file_id"] == intel_file_id for item in resurrected)

    detail = client.get(f"/api/v1/intel-files/{intel_file_id}")
    assert detail.status_code == 200
    data = detail.json()["data"]
    assert len(data["evidence"]) >= 2
    assert any(event["event_type"] == "status_changed" for event in data["timeline"])
