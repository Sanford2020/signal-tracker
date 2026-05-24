from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelEvent, IntelFile, LifecycleSnapshot, RawItem, Source, SourceType
from app.models.enums import IntelEventType, LifecycleStatus


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


def _evaluate(
    client: TestClient,
    intel_file_id: str,
    *,
    now: datetime | None = None,
) -> dict:
    body: dict = {"reason": "manual"}
    if now is not None:
        body["now"] = now.isoformat()
    response = client.post(f"/api/v1/intel-files/{intel_file_id}/evaluate", json=body)
    assert response.status_code == 200
    return response.json()["data"]


def _attach(
    client: TestClient,
    intel_file_id: str,
    raw_item_id: UUID,
    *,
    evidence_type: str = "follow_up",
) -> None:
    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={"raw_item_id": str(raw_item_id), "evidence_type": evidence_type},
    )
    assert response.status_code == 200


def test_evaluation_returns_required_response_shape(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    data = _evaluate(client, intel_file_id)

    assert "previous_status" in data
    assert "next_status" in data
    assert "reason" in data
    assert "evidence_ids" in data
    assert "score_changes" in data
    assert "heat_score" in data["score_changes"]
    assert len(data["score_changes"]["heat_score"]) == 2


def test_snapshot_created_on_every_evaluation(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Snapshot test", content="Body")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    _evaluate(client, intel_file_id)
    _evaluate(client, intel_file_id)

    count = db_session.scalar(
        select(func.count()).where(LifecycleSnapshot.intel_file_id == UUID(intel_file_id))
    )
    assert count == 2


def test_status_change_creates_intel_event(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Trackable signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    data = _evaluate(client, intel_file_id)
    assert data["previous_status"] == LifecycleStatus.NEW.value
    assert data["next_status"] == LifecycleStatus.WATCHING.value

    event = db_session.scalar(
        select(IntelEvent).where(
            IntelEvent.intel_file_id == UUID(intel_file_id),
            IntelEvent.event_type == IntelEventType.STATUS_CHANGED,
        )
    )
    assert event is not None
    assert "watching" in event.title.lower()


def test_no_op_evaluation_still_records_snapshot(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Trackable signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)
    _evaluate(client, intel_file_id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.WATCHING
    db_session.commit()

    data = _evaluate(client, intel_file_id)
    assert data["previous_status"] == LifecycleStatus.WATCHING.value
    assert data["next_status"] == LifecycleStatus.WATCHING.value

    snapshot_count = db_session.scalar(
        select(func.count()).where(LifecycleSnapshot.intel_file_id == UUID(intel_file_id))
    )
    assert snapshot_count == 2


def test_new_to_watching_transition(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Trackable signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    data = _evaluate(client, intel_file_id)
    assert data["next_status"] == LifecycleStatus.WATCHING.value
    assert "trackable" in data["reason"].lower()


def test_spreading_transition(client: TestClient, db_session: Session) -> None:
    first = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial.",
    )
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    for index in range(2):
        follow_up = _create_raw_item(
            db_session,
            title=f"Follow-up {index}",
            content="More evidence",
            source_name=f"Source {index}",
        )
        _attach(client, intel_file_id, follow_up.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.WATCHING
    db_session.commit()

    data = _evaluate(client, intel_file_id)
    assert data["next_status"] == LifecycleStatus.SPREADING.value


def test_dormant_transition_honors_configurable_threshold(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIFECYCLE_DORMANCY_DAYS", "7")
    from app.core.config import get_settings

    get_settings.cache_clear()

    raw_item = _create_raw_item(db_session, title="Dormant candidate", content="Old signal")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    now = datetime(2026, 6, 10, 12, 0, 0, tzinfo=UTC)
    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.WATCHING
    stored.last_seen_at = now - timedelta(days=10)
    db_session.commit()

    data = _evaluate(client, intel_file_id, now=now)
    assert data["next_status"] == LifecycleStatus.DORMANT.value
    assert "7 days" in data["reason"]


def test_dormant_file_with_new_evidence_becomes_resurrected(
    client: TestClient, db_session: Session
) -> None:
    first = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial.",
        captured_at=datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC),
    )
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.DORMANT
    stored.last_seen_at = datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC)
    db_session.commit()

    revival = _create_raw_item(
        db_session,
        title="Revival evidence",
        content="New update after dormancy",
        captured_at=datetime(2026, 5, 25, 12, 0, 0, tzinfo=UTC),
    )
    _attach(client, intel_file_id, revival.id, evidence_type="follow_up")

    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=UTC)
    data = _evaluate(client, intel_file_id, now=now)
    assert data["previous_status"] == LifecycleStatus.DORMANT.value
    assert data["next_status"] == LifecycleStatus.RESURRECTED.value
    assert data["evidence_ids"]


def test_verified_transition(client: TestClient, db_session: Session) -> None:
    first = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial.",
    )
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    corroboration = _create_raw_item(db_session, title="Official confirmation", content="Confirmed")
    _attach(client, intel_file_id, corroboration.id, evidence_type="corroboration")

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.credibility_score = 8.5
    stored.status = LifecycleStatus.VALIDATING
    db_session.commit()

    data = _evaluate(client, intel_file_id)
    assert data["next_status"] == LifecycleStatus.VERIFIED.value


def test_debunked_transition(client: TestClient, db_session: Session) -> None:
    first = _create_raw_item(db_session, title="Rumor signal", content="Unverified claim")
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    contradiction = _create_raw_item(db_session, title="Retraction", content="Claim withdrawn")
    _attach(client, intel_file_id, contradiction.id, evidence_type="contradiction")

    data = _evaluate(client, intel_file_id)
    assert data["next_status"] == LifecycleStatus.DEBUNKED.value


def test_noise_transition(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Low value chatter", content="Spammy")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.opportunity_score = 1.0
    stored.risk_score = 7.0
    stored.credibility_score = 5.0
    stored.status = LifecycleStatus.WATCHING
    db_session.commit()

    data = _evaluate(client, intel_file_id)
    assert data["next_status"] == LifecycleStatus.NOISE.value


def test_terminal_status_remains_unchanged(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Verified file", content="Done")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.VERIFIED
    db_session.commit()

    data = _evaluate(client, intel_file_id)
    assert data["previous_status"] == LifecycleStatus.VERIFIED.value
    assert data["next_status"] == LifecycleStatus.VERIFIED.value
    assert "terminal" in data["reason"].lower()

    event_count = db_session.scalar(
        select(func.count()).where(
            IntelEvent.intel_file_id == UUID(intel_file_id),
            IntelEvent.event_type == IntelEventType.STATUS_CHANGED,
        )
    )
    assert event_count == 0
