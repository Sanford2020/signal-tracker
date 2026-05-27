from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelFile, TrackingQuery
from app.models.enums import SignalType


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_analyzed_file(client: TestClient) -> str:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Example AI hiring hardware supply chain lead",
            "content": "Example AI is hiring for hardware supply chain leadership.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]

    analyze = client.post(f"/api/v1/raw-items/{raw_item_id}/analyze")
    assert analyze.status_code == 200

    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def test_generate_tracking_queries_from_analysis_and_file(client: TestClient, db_session: Session) -> None:
    intel_file_id = _create_analyzed_file(client)
    response = client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["created_count"] > 0
    assert len(data["items"]) >= 3
    queries = [item["query"] for item in data["items"]]
    assert any("Example AI hardware hiring" in query for query in queries)
    assert any(item["enabled"] is True for item in data["items"])

    stored = db_session.scalars(
        select(TrackingQuery).where(TrackingQuery.intel_file_id == UUID(intel_file_id))
    ).all()
    assert len(stored) == len(data["items"])


def test_generate_tracking_queries_is_idempotent(client: TestClient) -> None:
    intel_file_id = _create_analyzed_file(client)
    first = client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={})
    second = client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["data"]["created_count"] == 0
    first_queries = {item["normalized_query"] for item in first.json()["data"]["items"]}
    second_queries = {item["normalized_query"] for item in second.json()["data"]["items"]}
    assert first_queries == second_queries


def test_regenerate_replaces_queries_without_duplicates(client: TestClient, db_session: Session) -> None:
    intel_file_id = _create_analyzed_file(client)
    client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={})
    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/tracking-queries",
        json={"regenerate": True, "limit": 5},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) <= 5
    normalized = [item["normalized_query"] for item in data["items"]]
    assert len(normalized) == len(set(normalized))
    stored_count = len(
        db_session.scalars(
            select(TrackingQuery).where(TrackingQuery.intel_file_id == UUID(intel_file_id))
        ).all()
    )
    assert stored_count == len(data["items"])


def test_tracking_queries_include_source_hints(client: TestClient) -> None:
    intel_file_id = _create_analyzed_file(client)
    response = client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={})

    assert response.status_code == 200
    hints = {item["source_hint"] for item in response.json()["data"]["items"]}
    assert "careers" in hints


def test_research_tracking_queries_use_research_source_hint(client: TestClient, db_session: Session) -> None:
    intel_file_id = _create_analyzed_file(client)
    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.primary_signal_type = SignalType.RESEARCH
    db_session.commit()

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/tracking-queries",
        json={"regenerate": True},
    )

    assert response.status_code == 200
    hints = {item["source_hint"] for item in response.json()["data"]["items"]}
    assert "research" in hints


@pytest.mark.parametrize(
    ("signal_type", "expected_hint"),
    [
        (SignalType.FUNDING, "funding"),
        (SignalType.MARKET, "market"),
        (SignalType.POLICY, "policy"),
    ],
)
def test_news_adjacent_tracking_queries_keep_specific_source_hints(
    client: TestClient,
    db_session: Session,
    signal_type: SignalType,
    expected_hint: str,
) -> None:
    intel_file_id = _create_analyzed_file(client)
    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.primary_signal_type = signal_type
    db_session.commit()

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/tracking-queries",
        json={"regenerate": True},
    )

    assert response.status_code == 200
    hints = {item["source_hint"] for item in response.json()["data"]["items"]}
    assert expected_hint in hints


def test_package_signals_generate_pypi_tracking_hint(client: TestClient, db_session: Session) -> None:
    intel_file_id = _create_analyzed_file(client)
    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.title = "OpenAI Python SDK package release"
    intel_file.thesis = "Watch package releases for SDK ecosystem movement."
    intel_file.primary_signal_type = SignalType.PRODUCT
    intel_file.keywords = ["python", "sdk", "package"]
    db_session.commit()

    response = client.post(
        f"/api/v1/intel-files/{intel_file_id}/tracking-queries",
        json={"regenerate": True},
    )

    assert response.status_code == 200
    pypi_items = [item for item in response.json()["data"]["items"] if item["source_hint"] == "pypi"]
    assert pypi_items
    assert pypi_items[0]["rationale"] == "Python package or SDK release tracking."


def test_generate_tracking_queries_missing_file_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/intel-files/00000000-0000-0000-0000-000000000001/tracking-queries",
        json={},
    )
    assert response.status_code == 404
