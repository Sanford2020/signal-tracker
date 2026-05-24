from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import IntelFile, TrendArchiveSnapshot
from app.models.enums import LifecycleStatus


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_file(client: TestClient, title: str = "Example AI funding signal") -> str:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": title,
            "content": f"{title} appears in a new funding signal.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def test_run_trend_archive_snapshots_creates_daily_rows(
    client: TestClient,
    db_session: Session,
) -> None:
    first_id = _create_file(client, "First archive signal")
    second_id = _create_file(client, "Second archive signal")

    response = client.post(
        "/api/v1/archives/snapshots/run",
        json={"archive_date": "2026-05-24"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["archive_date"] == "2026-05-24"
    assert data["checked_count"] == 2
    assert data["created_count"] == 2
    assert data["updated_count"] == 0
    assert {item["intel_file_id"] for item in data["items"]} == {first_id, second_id}
    assert len(db_session.scalars(select(TrendArchiveSnapshot)).all()) == 2


def test_run_trend_archive_snapshots_is_idempotent_and_updates_state(
    client: TestClient,
    db_session: Session,
) -> None:
    intel_file_id = _create_file(client)
    first = client.post(
        "/api/v1/archives/snapshots/run",
        json={"archive_date": "2026-05-24"},
    )
    assert first.status_code == 200

    intel_file = db_session.get(IntelFile, UUID(intel_file_id))
    assert intel_file is not None
    intel_file.status = LifecycleStatus.VERIFIED
    intel_file.heat_score = 8.5
    db_session.commit()

    second = client.post(
        "/api/v1/archives/snapshots/run",
        json={"archive_date": "2026-05-24"},
    )

    assert second.status_code == 200
    data = second.json()["data"]
    assert data["created_count"] == 0
    assert data["updated_count"] == 1
    assert data["items"][0]["status"] == "verified"
    assert data["items"][0]["heat_score"] == 8.5
    snapshots = db_session.scalars(select(TrendArchiveSnapshot)).all()
    assert len(snapshots) == 1


def test_list_trend_archive_snapshots_returns_chronological_history(
    client: TestClient,
) -> None:
    intel_file_id = _create_file(client)
    for archive_date in ["2026-05-22", "2026-05-24", "2026-05-23"]:
        response = client.post(
            "/api/v1/archives/snapshots/run",
            json={"archive_date": archive_date},
        )
        assert response.status_code == 200

    response = client.get(f"/api/v1/intel-files/{intel_file_id}/trend")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 3
    assert [item["archive_date"] for item in data["items"]] == [
        "2026-05-22",
        "2026-05-23",
        "2026-05-24",
    ]


def test_list_trend_archive_snapshots_missing_file_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/v1/intel-files/00000000-0000-0000-0000-000000000001/trend"
    )

    assert response.status_code == 404
