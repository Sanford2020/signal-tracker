import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import RawItem, Source, SourceType


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def test_submit_text_creates_raw_item(client: TestClient) -> None:
    response = client.post(
        "/api/v1/inbox/submit",
        json={"title": "Funding rumor", "content": "Company X may raise Series B."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["duplicate"] is False
    assert payload["data"]["raw_item"]["title"] == "Funding rumor"
    assert payload["data"]["raw_item"]["content"] == "Company X may raise Series B."


def test_submit_url_only_allows_null_content(client: TestClient) -> None:
    response = client.post(
        "/api/v1/inbox/submit",
        json={"url": "https://example.com/signal-post"},
    )
    assert response.status_code == 200
    raw_item = response.json()["data"]["raw_item"]
    assert raw_item["url"] == "https://example.com/signal-post"
    assert raw_item["content"] is None


def test_manual_source_fallback(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/api/v1/inbox/submit",
        json={"content": "Manual pasted signal"},
    )
    assert response.status_code == 200
    source = db_session.scalar(
        select(Source).where(Source.source_type == SourceType.MANUAL, Source.name == "Manual Intake")
    )
    assert source is not None
    assert source.source_type == SourceType.MANUAL
    assert source.name == "Manual Intake"


def test_duplicate_hash_returns_existing_item(client: TestClient, db_session: Session) -> None:
    first = client.post(
        "/api/v1/inbox/submit",
        json={"url": "https://example.com/dup", "content": "same body"},
    )
    assert first.status_code == 200
    first_id = first.json()["data"]["raw_item"]["id"]

    second = client.post(
        "/api/v1/inbox/submit",
        json={"url": "https://example.com/dup", "content": "same body"},
    )
    assert second.status_code == 200
    body = second.json()
    assert body["success"] is True
    assert body["data"]["duplicate"] is True
    assert body["data"]["raw_item"]["id"] == first_id
    count = db_session.scalar(select(func.count()).select_from(RawItem))
    assert count == 1


def test_list_inbox_shows_pending_analysis(client: TestClient) -> None:
    client.post("/api/v1/inbox/submit", json={"content": "Pending analysis item"})

    response = client.get("/api/v1/inbox")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1
    assert data["items"][0]["analysis_status"] == "pending"
    assert data["items"][0]["has_intel_file"] is False


def test_submit_requires_at_least_one_field(client: TestClient) -> None:
    response = client.post("/api/v1/inbox/submit", json={})
    assert response.status_code == 422
    detail = response.json()["detail"]
    message = " ".join(item["msg"] for item in detail)
    assert "at least one" in message.lower()


def test_submit_whitespace_only_returns_validation_error(client: TestClient) -> None:
    response = client.post(
        "/api/v1/inbox/submit",
        json={"url": " ", "title": " ", "content": " "},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    message = " ".join(item["msg"] for item in detail)
    assert "at least one" in message.lower()
