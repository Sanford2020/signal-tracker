import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelFile, RawItem, SignalAnalysis, Source, SourceType
from app.models.enums import LifecycleStatus
from app.modules.extraction.normalize import ExtractionError, normalize_extraction_output
from app.modules.extraction.mock import MockExtractor
from app.modules.extraction.schemas import ExtractionInput, ExtractionSourceContext


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


def test_mock_extract_hiring_signal_is_deterministic() -> None:
    extractor = MockExtractor()
    input_data = ExtractionInput(
        title="Example AI hiring hardware supply chain lead",
        content="Example AI is hiring for hardware supply chain leadership.",
        source=ExtractionSourceContext(name="Manual", source_type="manual", trust_tier=2),
        captured_at=_create_captured_at(),
    )

    first, _ = extractor.extract(input_data)
    second, _ = extractor.extract(input_data)

    assert first.signal_type == "hiring"
    assert first.model_dump() == second.model_dump()
    assert any(entity.get("name") == "Example AI" for entity in first.entities)
    assert "hardware" in first.keywords
    assert first.novelty_score >= 6
    assert 4 <= (first.credibility_hint or 0) <= 7


def test_analyze_raw_item_persists_signal_analysis(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(
        db_session,
        title="Example AI hiring hardware supply chain lead",
        content="Hiring post for hardware supply chain lead.",
    )

    response = client.post(f"/api/v1/raw-items/{raw_item.id}/analyze")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    analysis = payload["data"]["analysis"]
    assert analysis["signal_type"] == "hiring"
    assert analysis["prompt_version"] == "signal_extract_v1"
    assert analysis["model"] == "mock"
    assert analysis["suggested_tracking_queries"]
    assert analysis["rationale"]

    stored = db_session.scalar(select(SignalAnalysis).where(SignalAnalysis.raw_item_id == raw_item.id))
    assert stored is not None
    assert stored.summary == analysis["summary"]


def test_analyze_is_idempotent(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Funding rumor", content="Series B funding rumor")
    first = client.post(f"/api/v1/raw-items/{raw_item.id}/analyze")
    second = client.post(f"/api/v1/raw-items/{raw_item.id}/analyze")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["analysis"]["id"] == second.json()["data"]["analysis"]["id"]
    count = db_session.scalar(select(func.count()).select_from(SignalAnalysis))
    assert count == 1


def test_analyze_does_not_create_intel_file(client: TestClient, db_session: Session) -> None:
    raw_item = _create_raw_item(db_session, title="Generic signal", content="Some update")
    response = client.post(f"/api/v1/raw-items/{raw_item.id}/analyze")
    assert response.status_code == 200
    intel_count = db_session.scalar(select(func.count()).select_from(IntelFile))
    assert intel_count == 0


def test_analyze_succeeds_when_unrelated_intel_file_exists(
    client: TestClient, db_session: Session
) -> None:
    ts = _create_captured_at()
    db_session.add(
        IntelFile(
            title="Existing unrelated file",
            status=LifecycleStatus.WATCHING,
            first_seen_at=ts,
            last_seen_at=ts,
        )
    )
    db_session.commit()
    intel_count_before = db_session.scalar(select(func.count()).select_from(IntelFile))
    assert intel_count_before == 1

    raw_item = _create_raw_item(db_session, title="New signal", content="Fresh candidate signal")
    response = client.post(f"/api/v1/raw-items/{raw_item.id}/analyze")

    assert response.status_code == 200
    assert response.json()["success"] is True

    stored = db_session.scalar(
        select(SignalAnalysis).where(SignalAnalysis.raw_item_id == raw_item.id)
    )
    assert stored is not None

    intel_count_after = db_session.scalar(select(func.count()).select_from(IntelFile))
    assert intel_count_after == intel_count_before


def test_analyze_missing_raw_item_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/raw-items/00000000-0000-0000-0000-000000000001/analyze",
    )
    assert response.status_code == 404


def test_normalize_rejects_empty_summary() -> None:
    with pytest.raises(ExtractionError):
        normalize_extraction_output({"summary": "  ", "signal_type": "other"})


def _create_captured_at():
    from datetime import datetime

    return datetime(2026, 5, 23, 12, 0, 0)
