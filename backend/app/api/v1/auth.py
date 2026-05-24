from fastapi import APIRouter, Depends, Header
from fastapi.responses import Response
from sqlalchemy.orm import Session

from uuid import UUID

from app.api.v1.dependencies import (
    require_admin_rate_limit,
    require_admin_secret,
    require_workspace_access,
    require_workspace_admin,
)
from app.db.session import get_db
from app.modules.auth.service import add_workspace_member, bootstrap_workspace, list_workspace_members, list_workspaces
from app.modules.audit.service import export_audit_events_csv, list_audit_events
from app.schemas.api import ApiResponse
from app.schemas.audit import AuditEventListData
from app.schemas.auth import (
    BootstrapData,
    BootstrapRequest,
    WorkspaceListData,
    WorkspaceMemberCreateData,
    WorkspaceMemberCreateRequest,
    WorkspaceMemberListData,
)

router = APIRouter(tags=["auth"])


@router.post("/auth/bootstrap", response_model=ApiResponse[BootstrapData])
def bootstrap_workspace_route(
    payload: BootstrapRequest,
    _: None = Depends(require_admin_rate_limit),
    __: None = Depends(require_admin_secret),
    db: Session = Depends(get_db),
) -> ApiResponse[BootstrapData]:
    data = bootstrap_workspace(db, payload)
    return ApiResponse(success=True, data=data, error=None)


@router.get("/workspaces", response_model=ApiResponse[WorkspaceListData])
def list_workspaces_route(
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkspaceListData]:
    data = list_workspaces(db, user_email=x_user_email)
    return ApiResponse(success=True, data=data, error=None)


@router.get("/workspaces/{workspace_id}/members", response_model=ApiResponse[WorkspaceMemberListData])
def list_workspace_members_route(
    workspace_id: UUID,
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkspaceMemberListData]:
    require_workspace_access(db, workspace_id, x_user_email, x_user_token)
    data = list_workspace_members(db, workspace_id)
    return ApiResponse(success=True, data=data, error=None)


@router.post("/workspaces/{workspace_id}/members", response_model=ApiResponse[WorkspaceMemberCreateData])
def add_workspace_member_route(
    workspace_id: UUID,
    payload: WorkspaceMemberCreateRequest,
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkspaceMemberCreateData]:
    require_workspace_admin(db, workspace_id, x_user_email, x_user_token)
    data = add_workspace_member(db, workspace_id, payload, actor_email=x_user_email)
    return ApiResponse(success=True, data=data, error=None)


@router.get("/workspaces/{workspace_id}/audit-events", response_model=ApiResponse[AuditEventListData])
def list_workspace_audit_events_route(
    workspace_id: UUID,
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[AuditEventListData]:
    require_workspace_admin(db, workspace_id, x_user_email, x_user_token)
    data = list_audit_events(db, workspace_id=workspace_id)
    return ApiResponse(success=True, data=data, error=None)


@router.get("/workspaces/{workspace_id}/audit-events.csv")
def export_workspace_audit_events_csv_route(
    workspace_id: UUID,
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> Response:
    require_workspace_admin(db, workspace_id, x_user_email, x_user_token)
    csv_content = export_audit_events_csv(db, workspace_id=workspace_id)
    return Response(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="workspace-{workspace_id}-audit-events.csv"'},
    )
