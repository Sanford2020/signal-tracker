from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import Workspace


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _workspace(db_session: Session, name: str) -> Workspace:
    workspace = Workspace(name=name, slug=name.lower().replace(" ", "-"))
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)
    return workspace


def _headers(workspace: Workspace) -> dict[str, str]:
    return {"X-Workspace-Id": str(workspace.id), "X-User-Email": "analyst@example.com"}


def test_saved_views_can_be_created_listed_and_deleted(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    payload = {
        "name": "High Opportunity",
        "filters": {
            "query": "agents",
            "status": "watching",
            "sort": "opportunity_score",
            "order": "desc",
            "page_size": 50,
        },
    }

    created = client.post("/api/v1/intel-file-saved-views", json=payload, headers=_headers(workspace))

    assert created.status_code == 200
    item = created.json()["data"]["item"]
    assert item["name"] == "High Opportunity"
    assert item["slug"] == "high-opportunity"
    assert item["workspace_id"] == str(workspace.id)
    assert item["description"] == ""
    assert item["is_default"] is False
    assert item["last_used_at"] is None
    assert item["filters"] == payload["filters"]

    listed = client.get("/api/v1/intel-file-saved-views", headers=_headers(workspace))
    assert listed.status_code == 200
    assert listed.json()["data"]["total"] == 1
    assert listed.json()["data"]["items"][0]["id"] == item["id"]

    deleted = client.delete(f"/api/v1/intel-file-saved-views/{item['id']}", headers=_headers(workspace))
    assert deleted.status_code == 200
    assert deleted.json()["data"]["deleted_id"] == item["id"]

    relisted = client.get("/api/v1/intel-file-saved-views", headers=_headers(workspace))
    assert relisted.json()["data"]["total"] == 0


def test_saved_views_are_upserted_by_workspace_slug(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    headers = _headers(workspace)
    first = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "filters": {"query": "agents", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    second = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "filters": {"query": "robotics", "status": "new", "sort": "heat_score", "order": "asc", "page_size": 10},
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["item"]["id"] == second.json()["data"]["item"]["id"]
    listed = client.get("/api/v1/intel-file-saved-views", headers=headers)
    assert listed.json()["data"]["total"] == 1
    assert listed.json()["data"]["items"][0]["filters"]["query"] == "robotics"


def test_saved_views_can_be_renamed_and_updated_by_id(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    headers = _headers(workspace)
    created = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "description": "Daily high-signal sweep",
            "filters": {"query": "agents", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    view_id = created.json()["data"]["item"]["id"]

    updated = client.patch(
        f"/api/v1/intel-file-saved-views/{view_id}",
        headers=headers,
        json={
            "name": "AI Watchlist",
            "description": "Robotics heat check",
            "filters": {"query": "robotics", "status": "new", "sort": "heat_score", "order": "asc", "page_size": 10},
        },
    )

    assert updated.status_code == 200
    item = updated.json()["data"]["item"]
    assert item["id"] == view_id
    assert item["name"] == "AI Watchlist"
    assert item["slug"] == "ai-watchlist"
    assert item["description"] == "Robotics heat check"
    assert item["filters"]["query"] == "robotics"
    assert item["filters"]["sort"] == "heat_score"


def test_saved_view_rename_rejects_workspace_slug_conflict(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    headers = _headers(workspace)
    first = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "filters": {"query": "agents", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    second = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Research",
            "filters": {"query": "papers", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )

    conflict = client.patch(
        f"/api/v1/intel-file-saved-views/{second.json()['data']['item']['id']}",
        headers=headers,
        json={"name": "Watchlist"},
    )

    assert first.status_code == 200
    assert conflict.status_code == 409


def test_saved_views_have_one_default_per_workspace(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    headers = _headers(workspace)
    first = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "is_default": True,
            "filters": {"query": "agents", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    second = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Research",
            "is_default": True,
            "filters": {"query": "papers", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )

    listed = client.get("/api/v1/intel-file-saved-views", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    defaults = [item for item in listed.json()["data"]["items"] if item["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["name"] == "Research"


def test_saved_view_default_can_be_changed_by_patch(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    headers = _headers(workspace)
    first = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "filters": {"query": "agents", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    second = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Research",
            "is_default": True,
            "filters": {"query": "papers", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )

    updated = client.patch(
        f"/api/v1/intel-file-saved-views/{first.json()['data']['item']['id']}",
        headers=headers,
        json={"is_default": True},
    )
    listed = client.get("/api/v1/intel-file-saved-views", headers=headers)

    assert second.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["data"]["item"]["is_default"] is True
    defaults = [item for item in listed.json()["data"]["items"] if item["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["id"] == first.json()["data"]["item"]["id"]


def test_saved_view_use_updates_last_used_at(client: TestClient, db_session: Session) -> None:
    workspace = _workspace(db_session, "Alpha Team")
    headers = _headers(workspace)
    created = client.post(
        "/api/v1/intel-file-saved-views",
        headers=headers,
        json={
            "name": "Watchlist",
            "description": "Daily sweep",
            "filters": {"query": "agents", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    view_id = created.json()["data"]["item"]["id"]

    used = client.post(f"/api/v1/intel-file-saved-views/{view_id}/use", headers=headers)

    assert used.status_code == 200
    item = used.json()["data"]["item"]
    assert item["id"] == view_id
    assert item["description"] == "Daily sweep"
    assert item["last_used_at"] is not None


def test_saved_views_are_workspace_scoped(client: TestClient, db_session: Session) -> None:
    alpha = _workspace(db_session, "Alpha Team")
    beta = _workspace(db_session, "Beta Team")

    created = client.post(
        "/api/v1/intel-file-saved-views",
        headers=_headers(alpha),
        json={
            "name": "Alpha View",
            "filters": {"query": "alpha", "status": "", "sort": "updated_at", "order": "desc", "page_size": 20},
        },
    )
    assert created.status_code == 200

    beta_list = client.get("/api/v1/intel-file-saved-views", headers=_headers(beta))
    assert beta_list.status_code == 200
    assert beta_list.json()["data"]["total"] == 0

    beta_delete = client.delete(
        f"/api/v1/intel-file-saved-views/{UUID(created.json()['data']['item']['id'])}",
        headers=_headers(beta),
    )
    assert beta_delete.status_code == 404
