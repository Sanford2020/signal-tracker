import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_file(client: TestClient) -> None:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={"title": "Report export signal", "content": "Report export content."},
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    assert client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id}).status_code == 200


def test_daily_markdown_report_export(client: TestClient) -> None:
    _create_file(client)

    response = client.get("/api/v1/reports/daily.md")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "# Daily Intelligence Briefing" in response.text
    assert "Report export signal" in response.text


def test_weekly_markdown_report_export(client: TestClient) -> None:
    _create_file(client)

    response = client.get("/api/v1/reports/weekly.md")

    assert response.status_code == 200
    assert "# Weekly Intelligence Retrospective" in response.text


def test_daily_pdf_report_export(client: TestClient) -> None:
    _create_file(client)

    response = client.get("/api/v1/reports/daily.pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_weekly_pdf_report_export(client: TestClient) -> None:
    response = client.get("/api/v1/reports/weekly.pdf")

    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
