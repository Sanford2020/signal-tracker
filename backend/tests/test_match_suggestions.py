from collections.abc import Sequence
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import Evidence, MatchSuggestion, RawItem, TrackingQuery
from app.modules.source_checks.service import CheckerResult, run_source_checks
from app.schemas.source_checks import SourceCheckRunRequest


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_tracking_queries(client: TestClient) -> tuple[str, list[dict]]:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Northstar AI posts robotics procurement role",
            "content": "Northstar AI is hiring robotics procurement and supply chain operators.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    intel_file_id = create_file.json()["data"]["intel_file"]["id"]

    generated = client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={"limit": 3})
    assert generated.status_code == 200
    return intel_file_id, generated.json()["data"]["items"]


class MatchingChecker:
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        return [
            CheckerResult(
                title="Northstar AI robotics procurement follow-up",
                url="https://example.com/northstar-robotics-procurement",
                snippet="Northstar AI added more robotics procurement supply chain hiring details.",
                source_name="example-search",
            )
        ]


class UnrelatedChecker:
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        return [
            CheckerResult(
                title="Unrelated consumer finance market item",
                url="https://example.com/finance",
                snippet="A banking platform launched a cashback card.",
                source_name="example-search",
            )
        ]


def test_generate_match_suggestions_for_matching_source_results(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id, _ = _create_tracking_queries(client)
    run_data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=MatchingChecker())

    response = client.post(
        f"/api/v1/source-checks/runs/{run_data.run.id}/match-suggestions",
        json={"min_confidence": 0.65},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["created_count"] == 1
    item = data["items"][0]
    assert item["intel_file_id"] == intel_file_id
    assert item["confidence"] >= 0.65
    assert item["status"] == "open"
    assert "Matched terms" in item["rationale"]

    stored = db_session.scalars(select(MatchSuggestion)).all()
    assert len(stored) == 1


def test_low_overlap_results_do_not_create_suggestions(
    client: TestClient,
    db_session: Session,
) -> None:
    _create_tracking_queries(client)
    run_data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=UnrelatedChecker())

    response = client.post(
        f"/api/v1/source-checks/runs/{run_data.run.id}/match-suggestions",
        json={"min_confidence": 0.65},
    )

    assert response.status_code == 200
    assert response.json()["data"]["created_count"] == 0
    assert db_session.scalars(select(MatchSuggestion)).all() == []


def test_match_suggestions_are_idempotent(client: TestClient, db_session: Session) -> None:
    _create_tracking_queries(client)
    run_data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=MatchingChecker())
    path = f"/api/v1/source-checks/runs/{run_data.run.id}/match-suggestions"

    first = client.post(path, json={"min_confidence": 0.65})
    second = client.post(path, json={"min_confidence": 0.65})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["created_count"] == 1
    assert second.json()["data"]["created_count"] == 0
    assert len(db_session.scalars(select(MatchSuggestion)).all()) == 1


def test_list_open_match_suggestions_for_intel_file(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id, _ = _create_tracking_queries(client)
    run_data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=MatchingChecker())
    client.post(
        f"/api/v1/source-checks/runs/{run_data.run.id}/match-suggestions",
        json={"min_confidence": 0.65},
    )

    response = client.get(f"/api/v1/intel-files/{intel_file_id}/match-suggestions")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["result_title"] == "Northstar AI robotics procurement follow-up"


def test_list_match_suggestions_missing_file_returns_404(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/intel-files/{UUID('00000000-0000-0000-0000-000000000001')}/match-suggestions"
    )
    assert response.status_code == 404


def test_accept_match_suggestion_creates_raw_item_and_evidence(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id, _ = _create_tracking_queries(client)
    run_data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=MatchingChecker())
    generated = client.post(
        f"/api/v1/source-checks/runs/{run_data.run.id}/match-suggestions",
        json={"min_confidence": 0.65},
    )
    suggestion_id = generated.json()["data"]["items"][0]["id"]

    response = client.post(
        f"/api/v1/match-suggestions/{suggestion_id}/accept",
        json={"rationale": "Accepted by analyst."},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["item"]["status"] == "accepted"
    assert data["raw_item_id"] is not None
    assert data["evidence_id"] is not None

    raw_item = db_session.get(RawItem, UUID(data["raw_item_id"]))
    assert raw_item is not None
    assert raw_item.title == "Northstar AI robotics procurement follow-up"
    evidence = db_session.get(Evidence, UUID(data["evidence_id"]))
    assert evidence is not None
    assert evidence.intel_file_id == UUID(intel_file_id)
    assert evidence.raw_item_id == raw_item.id


def test_accept_match_suggestion_is_idempotent(
    client: TestClient,
    db_session: Session,
) -> None:
    _create_tracking_queries(client)
    run_data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=MatchingChecker())
    generated = client.post(
        f"/api/v1/source-checks/runs/{run_data.run.id}/match-suggestions",
        json={"min_confidence": 0.65},
    )
    suggestion_id = generated.json()["data"]["items"][0]["id"]
    path = f"/api/v1/match-suggestions/{suggestion_id}/accept"

    first = client.post(path, json={})
    second = client.post(path, json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["raw_item_id"] == second.json()["data"]["raw_item_id"]
    assert first.json()["data"]["evidence_id"] == second.json()["data"]["evidence_id"]
    assert len(db_session.scalars(select(Evidence)).all()) == 2


def test_accept_missing_match_suggestion_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/match-suggestions/00000000-0000-0000-0000-000000000001/accept",
        json={},
    )
    assert response.status_code == 404
