from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelFile
from app.models.enums import LifecycleStatus


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_file(client: TestClient, title: str) -> str:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": title,
            "content": f"{title} has a meaningful weekly retrospective signal.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def test_weekly_retrospective_empty_state(client: TestClient) -> None:
    response = client.get("/api/v1/briefings/weekly")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["meta"]["window_days"] == 7
    assert data["meta"]["item_count"] == 0


def test_weekly_retrospective_sections(client: TestClient, db_session: Session) -> None:
    resurrected_id = _create_file(client, "Weekly resurrected signal")
    verified_id = _create_file(client, "Weekly verified signal")
    opportunity_id = _create_file(client, "Weekly opportunity signal")
    noise_id = _create_file(client, "Weekly noise signal")

    resurrected_file = db_session.get(IntelFile, UUID(resurrected_id))
    assert resurrected_file is not None
    resurrected_file.status = LifecycleStatus.DORMANT
    db_session.commit()
    resurrect = client.post(
        f"/api/v1/intel-files/{resurrected_id}/status",
        json={"status": "resurrected", "reason": "Renewed activity this week."},
    )
    assert resurrect.status_code == 200

    verified = client.post(
        f"/api/v1/intel-files/{verified_id}/status",
        json={"status": "verified", "reason": "Confirmed this week."},
    )
    assert verified.status_code == 200

    opportunity_file = db_session.get(IntelFile, UUID(opportunity_id))
    assert opportunity_file is not None
    opportunity_file.opportunity_score = 9.0

    noise_file = db_session.get(IntelFile, UUID(noise_id))
    assert noise_file is not None
    noise_file.status = LifecycleStatus.NOISE
    db_session.commit()

    response = client.get("/api/v1/briefings/weekly?days=7&min_opportunity=7")

    assert response.status_code == 200
    sections = response.json()["data"]["sections"]
    assert any(item["intel_file_id"] == resurrected_id for item in sections["changed_files"])
    assert any(item["intel_file_id"] == resurrected_id for item in sections["resurrected"])
    assert any(item["intel_file_id"] == verified_id for item in sections["verified_or_debunked"])
    assert any(item["intel_file_id"] == opportunity_id for item in sections["opportunity_gainers"])
    assert any(item["intel_file_id"] == noise_id for item in sections["cooling_or_noise"])
