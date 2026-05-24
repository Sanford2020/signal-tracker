from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import AlertEvent, IntelFile, RawItem, Source, SourceType
from app.models.enums import AlertStatus, AlertType, LifecycleStatus


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
    captured_at: datetime | None = None,
) -> RawItem:
    if source is None:
        source = _create_source(db_session, name="Manual Intake", trust_tier=2)
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


def _create_intel_file(client: TestClient, raw_item_id: UUID) -> str:
    response = client.post("/api/v1/intel-files", json={"raw_item_id": str(raw_item_id)})
    assert response.status_code == 200
    return response.json()["data"]["intel_file"]["id"]


def _attach(client: TestClient, intel_file_id: str, raw_item_id: UUID, evidence_type: str) -> None:
    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/evidence",
        json={"raw_item_id": str(raw_item_id), "evidence_type": evidence_type},
    )
    assert response.status_code == 200


def _evaluate(client: TestClient, intel_file_id: str, *, now: datetime | None = None) -> dict:
    body: dict = {"reason": "manual"}
    if now is not None:
        body["now"] = now.isoformat()
    response = client.post(f"/api/v1/intel-files/{intel_file_id}/evaluate", json=body)
    assert response.status_code == 200
    return response.json()["data"]


def _score(client: TestClient, intel_file_id: str) -> dict:
    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/score",
        json={"reason": "manual"},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_resurrected_transition_creates_alert(client: TestClient, db_session: Session) -> None:
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
        content="New update",
        captured_at=datetime(2026, 5, 25, 12, 0, 0, tzinfo=UTC),
    )
    _attach(client, intel_file_id, revival.id, "follow_up")

    _evaluate(client, intel_file_id, now=datetime(2026, 5, 26, 12, 0, 0, tzinfo=UTC))

    alert = db_session.scalar(
        select(AlertEvent).where(
            AlertEvent.intel_file_id == UUID(intel_file_id),
            AlertEvent.alert_type == AlertType.RESURRECTED,
        )
    )
    assert alert is not None
    assert alert.status == AlertStatus.PENDING


def test_opportunity_threshold_creates_alert(client: TestClient, db_session: Session) -> None:
    trusted = _create_source(db_session, name="Primary", trust_tier=0)
    first = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Strong signal.",
        source=trusted,
    )
    _analyze(client, first.id)
    intel_file_id = _create_intel_file(client, first.id)

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file_id)))
    assert stored is not None
    stored.opportunity_score = 6.0
    db_session.commit()

    for index in range(2):
        follow_up = _create_raw_item(
            db_session,
            title=f"Follow-up {index}",
            content="More evidence",
            source=_create_source(db_session, name=f"Source {index}", trust_tier=1),
        )
        _attach(client, intel_file_id, follow_up.id, "corroboration")

    _score(client, intel_file_id)

    alert = db_session.scalar(
        select(AlertEvent).where(
            AlertEvent.intel_file_id == UUID(intel_file_id),
            AlertEvent.alert_type == AlertType.OPPORTUNITY_UP,
        )
    )
    assert alert is not None


def test_duplicate_lifecycle_alert_is_not_created(client: TestClient, db_session: Session) -> None:
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
        content="New update",
        captured_at=datetime(2026, 5, 25, 12, 0, 0, tzinfo=UTC),
    )
    _attach(client, intel_file_id, revival.id, "follow_up")
    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=UTC)
    _evaluate(client, intel_file_id, now=now)
    _evaluate(client, intel_file_id, now=now)

    count = db_session.scalar(
        select(func.count()).where(
            AlertEvent.intel_file_id == UUID(intel_file_id),
            AlertEvent.alert_type == AlertType.RESURRECTED,
        )
    )
    assert count == 1


def test_list_alerts_returns_created_alert(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Debunk candidate", content="Rumor")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)

    contradiction = _create_raw_item(db_session, title="Retraction", content="Withdrawn")
    _attach(client, intel_file_id, contradiction.id, "contradiction")
    _evaluate(client, intel_file_id)

    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1
    assert data["items"][0]["intel_file_title"]
    assert data["items"][0]["severity"]
    assert data["items"][0]["message"]


def test_acknowledge_and_dismiss_alert(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Debunk candidate", content="Rumor")
    _analyze(client, raw_item.id)
    intel_file_id = _create_intel_file(client, raw_item.id)
    contradiction = _create_raw_item(db_session, title="Retraction", content="Withdrawn")
    _attach(client, intel_file_id, contradiction.id, "contradiction")
    _evaluate(client, intel_file_id)

    alert_id = db_session.scalar(select(AlertEvent.id).where(AlertEvent.intel_file_id == UUID(intel_file_id)))
    assert alert_id is not None

    ack = client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "acknowledged"})
    assert ack.status_code == 200
    assert ack.json()["data"]["status"] == "acknowledged"

    dismiss = client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "dismissed"})
    assert dismiss.status_code == 200
    assert dismiss.json()["data"]["status"] == "dismissed"
