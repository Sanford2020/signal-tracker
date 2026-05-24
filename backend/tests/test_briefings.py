from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelFile, RawItem, Source, SourceType
from app.models.enums import LifecycleStatus


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_source(db_session: Session, *, name: str = "Manual Intake", trust_tier: int = 2) -> Source:
    source = Source(name=name, source_type=SourceType.MANUAL, trust_tier=trust_tier)
    db_session.add(source)
    db_session.flush()
    return source


def _create_raw_item(
    db_session: Session,
    *,
    title: str,
    content: str = "Signal body",
    captured_at: datetime | None = None,
    source: Source | None = None,
) -> RawItem:
    if source is None:
        source = _create_source(db_session, name=f"Source {title}")
    raw_item = RawItem(
        source_id=source.id,
        title=title,
        content=content,
        content_hash=f"hash-{title}-{source.name}",
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


def _create_file(client: TestClient, raw_item_id: UUID) -> str:
    response = client.post("/api/v1/intel-files", json={"raw_item_id": str(raw_item_id)})
    assert response.status_code == 200
    return response.json()["data"]["intel_file"]["id"]


def _attach(client: TestClient, intel_file_id: str, raw_item_id: UUID, evidence_type: str = "follow_up") -> None:
    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={"raw_item_id": str(raw_item_id), "evidence_type": evidence_type},
    )
    assert response.status_code == 200


def _score(client: TestClient, intel_file_id: str) -> None:
    response = client.post(f"/api/v1/intel-files/{intel_file_id}/score", json={"reason": "test"})
    assert response.status_code == 200


def _evaluate(client: TestClient, intel_file_id: str, now: datetime | None = None) -> None:
    body: dict = {"reason": "test"}
    if now is not None:
        body["now"] = now.isoformat()
    response = client.post(f"/api/v1/intel-files/{intel_file_id}/evaluate", json=body)
    assert response.status_code == 200


def test_daily_briefing_empty_state(client: TestClient) -> None:
    response = client.get("/api/v1/briefings/daily")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["meta"]["window_hours"] == 24
    assert data["meta"]["item_count"] == 0
    assert "0 new files" in data["overview"]


def test_daily_briefing_includes_new_file(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="New signal")
    _analyze(client, raw_item.id)
    intel_file_id = _create_file(client, raw_item.id)

    response = client.get("/api/v1/briefings/daily")
    assert response.status_code == 200
    new_files = response.json()["data"]["sections"]["new_files"]
    assert any(item["intel_file_id"] == intel_file_id for item in new_files)
    assert new_files[0]["key_evidence"]


def test_daily_briefing_includes_updated_file(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Updated seed")
    _analyze(client, raw_item.id)
    intel_file_id = _create_file(client, raw_item.id)
    follow_up = _create_raw_item(db_session, title="Updated follow-up")
    _attach(client, intel_file_id, follow_up.id)

    response = client.get("/api/v1/briefings/daily")
    updated = response.json()["data"]["sections"]["updated_files"]
    assert any(item["intel_file_id"] == intel_file_id for item in updated)


def test_daily_briefing_includes_resurrected_file(client: TestClient, db_session: Session) -> None:
    old_time = datetime.now(UTC) - timedelta(days=40)
    raw_item = _create_raw_item(db_session, title="Dormant seed", captured_at=old_time)
    _analyze(client, raw_item.id)
    intel_file_id = _create_file(client, raw_item.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.status = LifecycleStatus.DORMANT
    stored.last_seen_at = old_time
    db_session.commit()

    revival = _create_raw_item(db_session, title="Revival update")
    _attach(client, intel_file_id, revival.id)
    _evaluate(client, intel_file_id)

    response = client.get("/api/v1/briefings/daily")
    resurrected = response.json()["data"]["sections"]["resurrected"]
    assert any(item["intel_file_id"] == intel_file_id for item in resurrected)


def test_daily_briefing_includes_high_opportunity(client: TestClient, db_session: Session) -> None:
    trusted = _create_source(db_session, name="Trusted", trust_tier=0)
    raw_item = _create_raw_item(db_session, title="Opportunity seed", source=trusted)
    _analyze(client, raw_item.id)
    intel_file_id = _create_file(client, raw_item.id)
    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.opportunity_score = 7.5
    db_session.commit()

    response = client.get("/api/v1/briefings/daily?min_opportunity=7")
    high_opp = response.json()["data"]["sections"]["high_opportunity"]
    assert any(item["intel_file_id"] == intel_file_id for item in high_opp)


def test_daily_briefing_includes_risk_or_noise_candidate(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Risk seed")
    _analyze(client, raw_item.id)
    intel_file_id = _create_file(client, raw_item.id)
    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.risk_score = 8.0
    db_session.commit()

    response = client.get("/api/v1/briefings/daily")
    risky = response.json()["data"]["sections"]["risk_or_noise"]
    assert any(item["intel_file_id"] == intel_file_id for item in risky)
