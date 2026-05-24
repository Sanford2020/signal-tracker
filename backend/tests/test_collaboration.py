from uuid import UUID

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


def _bootstrap(client: TestClient) -> tuple[str, str]:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={"email": "owner@example.com", "name": "Owner", "workspace_name": "Owner Workspace"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    return data["user"]["id"], data["workspace"]["id"]


def _create_file(client: TestClient, workspace_id: str) -> str:
    headers = {"X-Workspace-Id": workspace_id}
    submit = client.post(
        "/api/v1/inbox/submit",
        headers=headers,
        json={"title": "Team collaboration signal", "content": "Team collaboration content."},
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    return create_file.json()["data"]["intel_file"]["id"]


def test_update_collaboration_metadata(client: TestClient) -> None:
    user_id, workspace_id = _bootstrap(client)
    file_id = _create_file(client, workspace_id)

    response = client.patch(
        f"/api/v1/intel-files/{file_id}/collaboration",
        headers={"X-Workspace-Id": workspace_id},
        json={"owner_user_id": user_id, "review_note": "Reviewed by owner.", "mark_reviewed": True},
    )

    assert response.status_code == 200
    item = response.json()["data"]["item"]
    assert item["owner_user_id"] == user_id
    assert item["review_note"] == "Reviewed by owner."
    assert item["last_reviewed_at"] is not None

    detail = client.get(f"/api/v1/intel-files/{file_id}", headers={"X-Workspace-Id": workspace_id})
    assert detail.status_code == 200
    assert detail.json()["data"]["intel_file"]["owner_user_id"] == user_id


def test_create_and_list_comments(client: TestClient) -> None:
    _, workspace_id = _bootstrap(client)
    file_id = _create_file(client, workspace_id)
    headers = {"X-Workspace-Id": workspace_id, "X-User-Email": "owner@example.com"}

    created = client.post(
        f"/api/v1/intel-files/{file_id}/comments",
        headers=headers,
        json={"body": "This signal needs follow-up."},
    )

    assert created.status_code == 200
    item = created.json()["data"]["item"]
    assert item["author_email"] == "owner@example.com"
    assert item["body"] == "This signal needs follow-up."

    listed = client.get(f"/api/v1/intel-files/{file_id}/comments", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["data"]["total"] == 1


def test_comment_requires_known_author(client: TestClient) -> None:
    _, workspace_id = _bootstrap(client)
    file_id = _create_file(client, workspace_id)

    response = client.post(
        f"/api/v1/intel-files/{file_id}/comments",
        headers={"X-Workspace-Id": workspace_id, "X-User-Email": "missing@example.com"},
        json={"body": "No author."},
    )

    assert response.status_code == 401


def test_collaboration_respects_workspace_scope(client: TestClient) -> None:
    user_id, first_workspace = _bootstrap(client)
    second = client.post(
        "/api/v1/auth/bootstrap",
        json={"email": "second@example.com", "name": "Second", "workspace_name": "Second Workspace"},
    )
    assert second.status_code == 200
    second_workspace = second.json()["data"]["workspace"]["id"]
    file_id = _create_file(client, first_workspace)

    response = client.patch(
        f"/api/v1/intel-files/{file_id}/collaboration",
        headers={"X-Workspace-Id": second_workspace},
        json={"owner_user_id": user_id, "review_note": "Wrong workspace.", "mark_reviewed": True},
    )

    assert response.status_code == 404
