import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.main import app
from app.models import Evidence, IntelEvent, IntelFile, RawItem, SignalAnalysis, Source, SourceType
from app.models.enums import EvidenceType, IntelEventType, LifecycleStatus


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_raw_item(db_session: Session, *, title: str, content: str | None = None) -> RawItem:
    source = Source(name="Manual Intake", source_type=SourceType.MANUAL, trust_tier=2)
    db_session.add(source)
    db_session.flush()
    raw_item = RawItem(
        source_id=source.id,
        title=title,
        content=content,
        content_hash=f"hash-{title}",
    )
    db_session.add(raw_item)
    db_session.commit()
    db_session.refresh(raw_item)
    return raw_item


def _analyze(client: TestClient, raw_item_id) -> dict:
    response = client.post(f"/api/v1/raw-items/{raw_item_id}/analyze")
    assert response.status_code == 200
    return response.json()["data"]["analysis"]


def test_create_intel_file_from_analyzed_raw_item(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Hiring post for hardware supply chain lead.",
    )
    analysis = _analyze(client, raw_item.id)

    response = client.post(
        "/api/v1/intel-files",
        json={"raw_item_id": str(raw_item.id), "analysis_id": str(analysis["id"])},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    intel_file = payload["data"]["intel_file"]
    assert intel_file["status"] == "new"
    assert intel_file["evidence_count"] == 1
    assert intel_file["source_count"] == 1
    assert intel_file["heat_score"] == 1.0
    assert intel_file["primary_signal_type"] == "hiring"
    assert intel_file["first_seen_at"]
    assert intel_file["last_seen_at"]

    stored = db_session.scalar(select(IntelFile).where(IntelFile.id == UUID(intel_file["id"])))
    assert stored is not None

    evidence = db_session.scalar(
        select(Evidence).where(
            Evidence.intel_file_id == stored.id,
            Evidence.raw_item_id == raw_item.id,
        )
    )
    assert evidence is not None
    assert evidence.evidence_type == EvidenceType.FIRST_SEEN

    event = db_session.scalar(
        select(IntelEvent).where(
            IntelEvent.intel_file_id == stored.id,
            IntelEvent.event_type == IntelEventType.CREATED,
        )
    )
    assert event is not None
    assert event.source_evidence_id == evidence.id


def test_unanalyzed_raw_item_promotion_fails(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Not analyzed", content="Pending signal")

    response = client.post("/api/v1/intel-files", json={"raw_item_id": str(raw_item.id)})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert "signal analysis" in body["error"]["message"].lower()
    assert db_session.scalar(select(func.count()).select_from(IntelFile)) == 0


def test_duplicate_promotion_is_idempotent(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Funding rumor", content="Series B funding rumor")
    analysis = _analyze(client, raw_item.id)
    body = {"raw_item_id": str(raw_item.id), "analysis_id": str(analysis["id"])}

    first = client.post("/api/v1/intel-files", json=body)
    second = client.post("/api/v1/intel-files", json=body)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["intel_file"]["id"] == second.json()["data"]["intel_file"]["id"]
    assert db_session.scalar(select(func.count()).select_from(IntelFile)) == 1
    assert db_session.scalar(select(func.count()).select_from(Evidence)) == 1
    assert db_session.scalar(select(func.count()).select_from(IntelEvent)) == 1


def test_intel_file_list_returns_created_file(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Product launch rumor", content="Launch soon")
    _analyze(client, raw_item.id)
    created = client.post("/api/v1/intel-files", json={"raw_item_id": str(raw_item.id)})
    assert created.status_code == 200
    created_id = created.json()["data"]["intel_file"]["id"]

    response = client.get("/api/v1/intel-files")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["id"] == created_id
    assert data["items"][0]["title"] == raw_item.title


def test_intel_file_list_supports_search_status_sort_and_pagination(
    client: TestClient,
    db_session: Session,
) -> None:
    first_raw = _create_raw_item(db_session, title="Alpha robotics hiring", content="Hiring signal")
    second_raw = _create_raw_item(db_session, title="Beta model launch", content="Product signal")
    _analyze(client, first_raw.id)
    _analyze(client, second_raw.id)
    first = client.post("/api/v1/intel-files", json={"raw_item_id": str(first_raw.id)})
    second = client.post("/api/v1/intel-files", json={"raw_item_id": str(second_raw.id)})
    assert first.status_code == 200
    assert second.status_code == 200

    first_file = db_session.get(IntelFile, UUID(first.json()["data"]["intel_file"]["id"]))
    second_file = db_session.get(IntelFile, UUID(second.json()["data"]["intel_file"]["id"]))
    assert first_file is not None
    assert second_file is not None
    first_file.status = LifecycleStatus.WATCHING
    first_file.opportunity_score = 5.0
    second_file.status = LifecycleStatus.WATCHING
    second_file.opportunity_score = 9.0
    db_session.commit()

    searched = client.get("/api/v1/intel-files?q=robotics")
    assert searched.status_code == 200
    assert searched.json()["data"]["total"] == 1
    assert searched.json()["data"]["items"][0]["title"] == "Alpha robotics hiring"

    sorted_response = client.get(
        "/api/v1/intel-files?status=watching&sort=opportunity_score&order=desc&page=1&page_size=1"
    )
    assert sorted_response.status_code == 200
    sorted_data = sorted_response.json()["data"]
    assert sorted_data["total"] == 2
    assert sorted_data["items"][0]["title"] == "Beta model launch"


def test_intel_file_detail_returns_expected_fields(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Hiring post.",
    )
    analysis = _analyze(client, raw_item.id)
    created = client.post(
        "/api/v1/intel-files",
        json={
            "raw_item_id": str(raw_item.id),
            "analysis_id": str(analysis["id"]),
            "thesis": "Possible hardware expansion.",
        },
    )
    intel_file_id = created.json()["data"]["intel_file"]["id"]

    response = client.get(f"/api/v1/intel-files/{intel_file_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["intel_file"]["title"] == raw_item.title
    assert data["intel_file"]["thesis"] == "Possible hardware expansion."
    assert data["intel_file"]["status"] == LifecycleStatus.NEW.value
    assert data["intel_file"]["entities"]
    assert data["intel_file"]["keywords"]
    assert data["novelty_score"] is not None
    assert data["intel_file"]["credibility_score"] is not None
    assert len(data["evidence"]) == 1
    assert len(data["timeline"]) == 1


def test_analyze_endpoint_still_does_not_create_intel_file(
    client: TestClient, db_session: Session
) -> None:
    raw_item = _create_raw_item(db_session, title="Analyze only", content="No promotion")
    response = client.post(f"/api/v1/raw-items/{raw_item.id}/analyze")
    assert response.status_code == 200
    assert db_session.scalar(select(func.count()).select_from(IntelFile)) == 0
    assert db_session.scalar(select(func.count()).select_from(SignalAnalysis)) == 1
