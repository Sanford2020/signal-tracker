from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.usage.service import get_usage_summary
from app.schemas.api import ApiResponse
from app.schemas.usage import UsageSummaryData

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/summary", response_model=ApiResponse[UsageSummaryData])
def get_usage_summary_route(
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[UsageSummaryData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = get_usage_summary(db, workspace_id=x_workspace_id)
    return ApiResponse(success=True, data=data, error=None)
