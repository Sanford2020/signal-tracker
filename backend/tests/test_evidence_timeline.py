from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import Evidence, IntelEvent, IntelFile, RawItem, Source, SourceType
from app.models.enums import AttachedBy, EvidenceType, IntelEventType


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_raw_item(
    db_session: Session,
    *,
    title: str,
    content: str | None = None,
    source_name: str = "Manual Intake",
    captured_at: datetime | None = None,
) -> RawItem:
    source = db_session.scalar(
        select(Source).where(Source.name == source_name, Source.source_type == SourceType.MANUAL)
    )
    if source is None:
        source = Source(name=source_name, source_type=SourceType.MANUAL, trust_tier=2)
        db_session.add(source)
        db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title=title,
        content=content,
        content_hash=f"hash-{title}-{source_name}",
    )
    if captured_at is not None:
        raw_item.captured_at = captured_at
    db_session.add(raw_item)
    db_session.commit()
    db_session.refresh(raw_item)
    return raw_item


def _analyze(client: TestClient, raw_item_id: UUID) -> None:
    response = client.post(f"/api/v1/raw-items/{raw_item_id}/analyze")
    assert response.status_code == 200


def _create_intel_file(client: TestClient, raw_item_id: UUID) -> str:
    response = client.post("/api/v1/intel-files", json={"raw_item_id": str(raw_item_id)})
    assert response.status_code == 200
    return response.json()["data"]["intel_file"]["id"]


def test_attach_follow_up_evidence_succeeds(client: TestClient, db_session: Session) -> None:
    first_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial hiring signal.",
        captured_at=datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC),
    )
    _analyze(client, first_item.id)
    intel_file_id = _create_intel_file(client, first_item.id)

    follow_up = _create_raw_item(
        db_session,
        title="Follow-up careers page update",
        content="Updated job listing.",
        source_name="Careers Feed",
        captured_at=datetime(2026, 5, 24, 12, 0, 0, tzinfo=UTC),
    )

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={
            "raw_item_id": str(follow_up.id),
            "evidence_type": "follow_up",
            "confidence": 0.82,
            "attached_by": "user",
            "rationale": "Same entity and claim; adds primary-source evidence.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["evidence"]["evidence_type"] == "follow_up"
    assert payload["data"]["evidence"]["attached_by"] == "user"
    assert payload["data"]["intel_file"]["evidence_count"] == 2
    assert payload["data"]["intel_file"]["source_count"] == 2

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    assert stored.evidence_count == 2
    assert stored.source_count == 2
    assert stored.last_seen_at == follow_up.captured_at


def test_attach_evidence_missing_intel_file_returns_404(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Orphan raw item", content="No file")
    response = client.post(
        "/api/v1/intel-files/00000000-0000-0000-0000-000000000001/evidence",
        json={"raw_item_id": str(raw_item.id), "evidence_type": "follow_up"},
    )
    assert response.status_code == 404


def test_attach_evidence_missing_raw_item_returns_404(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={
            "raw_item_id": "00000000-0000-0000-0000-000000000002",
            "evidence_type": "follow_up",
        },
    )
    assert response.status_code == 404


def test_duplicate_evidence_attachment_is_rejected(client: TestClient, db_session: Session) -> None:
    first_item = _create_raw_item(db_session, title="Seed signal", content="Seed")
    _analyze(client, first_item.id)
    intel_file_id = _create_intel_file(client, first_item.id)

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={
            "raw_item_id": str(first_item.id),
            "evidence_type": "follow_up",
            "rationale": "Duplicate attempt",
        },
    )
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "conflict"
    assert db_session.scalar(select(func.count()).select_from(Evidence)) == 1


def test_evidence_added_event_is_created(client: TestClient, db_session: Session) -> None:
    first_item = _create_raw_item(db_session, title="Seed signal", content="Seed")
    _analyze(client, first_item.id)
    intel_file_id = _create_intel_file(client, first_item.id)
    follow_up = _create_raw_item(db_session, title="Follow-up item", content="More detail")

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={
            "raw_item_id": str(follow_up.id),
            "evidence_type": "corroboration",
            "confidence": 0.9,
            "attached_by": "system",
            "rationale": "Corroborating source.",
        },
    )
    assert response.status_code == 200
    evidence_id = response.json()["data"]["evidence"]["id"]

    event = db_session.scalar(
        select(IntelEvent).where(
            IntelEvent.intel_file_id == UUID(intel_file_id),
            IntelEvent.event_type == IntelEventType.EVIDENCE_ADDED,
        )
    )
    assert event is not None
    assert event.source_evidence_id == UUID(evidence_id)
    assert event.description == "Corroborating source."


def test_detail_timeline_includes_created_and_evidence_added_in_order(
    client: TestClient, db_session: Session
) -> None:
    first_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial signal.",
        captured_at=datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC),
    )
    _analyze(client, first_item.id)
    intel_file_id = _create_intel_file(client, first_item.id)
    follow_up = _create_raw_item(
        db_session,
        title="Later follow-up",
        content="More evidence",
        captured_at=datetime(2026, 5, 25, 12, 0, 0, tzinfo=UTC),
    )
    attach = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={"raw_item_id": str(follow_up.id), "evidence_type": "follow_up"},
    )
    assert attach.status_code == 200

    detail = client.get(f"/api/v1/intel-files/{intel_file_id}")
    assert detail.status_code == 200
    timeline = detail.json()["data"]["timeline"]
    assert len(timeline) == 2
    assert timeline[0]["event_type"] == IntelEventType.CREATED.value
    assert timeline[1]["event_type"] == IntelEventType.EVIDENCE_ADDED.value
    assert timeline[0]["event_time"] <= timeline[1]["event_time"]
