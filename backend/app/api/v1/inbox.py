from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.inbox.service import list_inbox_items, submit_inbox_item
from app.modules.auth.service import ensure_workspace_exists
from app.schemas.api import ApiError, ApiResponse
from app.schemas.inbox import InboxListData, InboxSubmitData, InboxSubmitRequest

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.post("/submit", response_model=ApiResponse[InboxSubmitData])
def submit_signal(
    payload: InboxSubmitRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[InboxSubmitData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = submit_inbox_item(db, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=ApiResponse[InboxSubmitData](
                success=False,
                data=None,
                error=ApiError(code="validation_error", message=str(exc)),
            ).model_dump(),
        ) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.get("", response_model=ApiResponse[InboxListData])
def get_inbox(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    has_analysis: bool | None = Query(None),
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[InboxListData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = list_inbox_items(
        db,
        page=page,
        page_size=page_size,
        has_analysis=has_analysis,
        workspace_id=x_workspace_id,
    )
    return ApiResponse(success=True, data=data, error=None)
