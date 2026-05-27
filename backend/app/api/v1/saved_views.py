from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.saved_views.service import (
    delete_intel_file_saved_view,
    list_intel_file_saved_views,
    update_intel_file_saved_view,
    upsert_intel_file_saved_view,
)
from app.schemas.api import ApiResponse
from app.schemas.saved_views import (
    IntelFileSavedViewCreateRequest,
    IntelFileSavedViewData,
    IntelFileSavedViewDeleteData,
    IntelFileSavedViewListData,
    IntelFileSavedViewUpdateRequest,
)

router = APIRouter(prefix="/intel-file-saved-views", tags=["intel-file-saved-views"])


@router.get("", response_model=ApiResponse[IntelFileSavedViewListData])
def list_intel_file_saved_views_route(
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileSavedViewListData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = list_intel_file_saved_views(db, workspace_id=x_workspace_id)
    return ApiResponse(success=True, data=data, error=None)


@router.post("", response_model=ApiResponse[IntelFileSavedViewData])
def upsert_intel_file_saved_view_route(
    payload: IntelFileSavedViewCreateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileSavedViewData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = upsert_intel_file_saved_view(
        db,
        payload,
        workspace_id=x_workspace_id,
        actor_email=x_user_email,
    )
    return ApiResponse(success=True, data=data, error=None)


@router.patch("/{view_id}", response_model=ApiResponse[IntelFileSavedViewData])
def update_intel_file_saved_view_route(
    view_id: UUID,
    payload: IntelFileSavedViewUpdateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileSavedViewData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = update_intel_file_saved_view(
            db,
            view_id,
            payload,
            workspace_id=x_workspace_id,
            actor_email=x_user_email,
        )
    except ValueError as exc:
        status_code = 409 if "already exists" in str(exc) else 404
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.delete("/{view_id}", response_model=ApiResponse[IntelFileSavedViewDeleteData])
def delete_intel_file_saved_view_route(
    view_id: UUID,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileSavedViewDeleteData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = delete_intel_file_saved_view(db, view_id, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)
