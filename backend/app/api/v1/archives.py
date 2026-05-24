from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.archives.service import run_trend_archive_snapshots
from app.schemas.api import ApiResponse
from app.schemas.archives import TrendArchiveRunData, TrendArchiveRunRequest

router = APIRouter(prefix="/archives", tags=["archives"])


@router.post("/snapshots/run", response_model=ApiResponse[TrendArchiveRunData])
def run_trend_archive_snapshots_route(
    payload: TrendArchiveRunRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[TrendArchiveRunData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = run_trend_archive_snapshots(db, payload, workspace_id=x_workspace_id)
    return ApiResponse(success=True, data=data, error=None)
