import json
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelEvent, IntelFile, LifecycleSnapshot, RawItem, Source, SourceType
from app.models.enums import IntelEventType, LifecycleStatus
from app.modules.scoring.service import clamp_score


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_source(db_session: Session, *, name: str, trust_tier: int) -> Source:
    source = Source(name=name, source_type=SourceType.MANUAL, trust_tier=trust_tier)
    db_session.add(source)
    db_session.flush()
    return source


def _create_raw_item(
    db_session: Session,
    *,
    title: str,
    content: str | None = None,
    source: Source | None = None,
) -> RawItem:
    if source is None:
        source = _create_source(db_session, name="Manual Intake", trust_tier=2)
    raw_item = RawItem(
        source_id=source.id,
        title=title,
        content=content,
        content_hash=f"hash-{title}-{source.name}",
    )
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


def _score(client: TestClient, intel_file_id: str) -> dict:
    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/score",
        json={"reason": "manual"},
    )
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


def test_normal_scoring_updates_all_fields(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    data = _score(client, intel_file_id)

    assert 0 <= data["novelty_score"] <= 10
    assert 0 <= data["heat_score"] <= 10
    assert 0 <= data["credibility_score"] <= 10
    assert 0 <= data["opportunity_score"] <= 10
    assert 0 <= data["risk_score"] <= 10
    assert data["rationale"]
    assert data["inputs"]["evidence_count"] == 1
    assert "score_changes" in data

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    assert stored.heat_score == data["heat_score"]
    assert stored.opportunity_score == data["opportunity_score"]


def test_high_risk_increases_risk_score(client: TestClient, db_session: Session) -> None:
    low_trust = _create_source(db_session, name="Untrusted Feed", trust_tier=3)
    first = _create_raw_item(db_session, title="Rumor signal", content="Unverified", source=low_trust)
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    contradiction = _create_raw_item(
        db_session,
        title="Retraction",
        content="Claim withdrawn",
        source=low_trust,
    )
    _attach(client, intel_file_id, contradiction.id, evidence_type="contradiction")

    data = _score(client, intel_file_id)
    assert data["risk_score"] >= 6.0
    assert data["inputs"]["risk"]["contradiction_penalty"] >= 1.5


def test_corroboration_and_high_trust_increase_credibility(
    client: TestClient, db_session: Session
) -> None:
    trusted = _create_source(db_session, name="Primary Source", trust_tier=0)
    first = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Initial.",
        source=trusted,
    )
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    corroboration = _create_raw_item(
        db_session,
        title="Official confirmation",
        content="Confirmed",
        source=trusted,
    )
    _attach(client, intel_file_id, corroboration.id, evidence_type="corroboration")

    data = _score(client, intel_file_id)
    assert data["credibility_score"] >= 7.0
    assert data["inputs"]["credibility"]["corroboration_bonus"] >= 1.5


def test_high_opportunity_from_strong_analysis_signals(client: TestClient, db_session: Session) -> None:
    trusted = _create_source(db_session, name="Primary Source", trust_tier=0)
    first = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Strong hiring signal.",
        source=trusted,
    )
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    for index in range(2):
        follow_up = _create_raw_item(
            db_session,
            title=f"Follow-up {index}",
            content="More evidence",
            source=_create_source(db_session, name=f"Source {index}", trust_tier=1),
        )
        _attach(client, intel_file_id, follow_up.id, evidence_type="corroboration")

    data = _score(client, intel_file_id)
    assert data["opportunity_score"] >= 6.0
    assert data["inputs"]["opportunity"]["relevance"] >= 5.0


def test_low_credibility_with_untrusted_source(client: TestClient, db_session: Session) -> None:
    untrusted = _create_source(db_session, name="Low Trust", trust_tier=3)
    raw_item = _create_raw_item(
        db_session,
        title="Weak chatter",
        content="Unverified claim",
        source=untrusted,
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    data = _score(client, intel_file_id)
    assert data["credibility_score"] <= 5.0
    assert data["inputs"]["credibility"]["average_source_trust"] <= 3.0


def test_scores_are_clamped_to_valid_range() -> None:
    assert clamp_score(-5.0) == 0.0
    assert clamp_score(15.0) == 10.0
    assert clamp_score(6.789) == 6.8


def test_score_update_creates_snapshot_with_rationale(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Snapshot test", content="Body")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    _score(client, intel_file_id)

    snapshot = db_session.scalar(
        select(LifecycleSnapshot).where(LifecycleSnapshot.intel_file_id == UUID(intel_file_id))
    )
    assert snapshot is not None
    assert snapshot.reason
    payload = json.loads(snapshot.reason)
    assert payload["summary"]
    assert payload["novelty_score"] is not None
    assert payload["inputs"]


def test_scoring_does_not_change_lifecycle_status(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Trackable signal.",
    )
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.WATCHING
    db_session.commit()

    _score(client, intel_file_id)

    refreshed = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert refreshed is not None
    assert refreshed.status == LifecycleStatus.WATCHING

    event = db_session.scalar(
        select(IntelEvent).where(
            IntelEvent.intel_file_id == UUID(intel_file_id),
            IntelEvent.event_type == IntelEventType.SCORE_CHANGED,
        )
    )
    assert event is not None
