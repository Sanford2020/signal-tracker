from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.briefings.service import generate_daily_briefing, generate_weekly_retrospective
from app.schemas.api import ApiResponse
from app.schemas.briefings import DailyBriefingData, WeeklyRetrospectiveData

router = APIRouter(prefix="/briefings", tags=["briefings"])


@router.get("/daily", response_model=ApiResponse[DailyBriefingData])
def get_daily_briefing(
    hours: int = Query(24, ge=1, le=168),
    min_opportunity: float | None = Query(None, ge=0, le=10),
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[DailyBriefingData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = generate_daily_briefing(
        db,
        hours=hours,
        min_opportunity=min_opportunity,
        workspace_id=x_workspace_id,
    )
    return ApiResponse(success=True, data=data, error=None)


@router.get("/weekly", response_model=ApiResponse[WeeklyRetrospectiveData])
def get_weekly_retrospective(
    days: int = Query(7, ge=1, le=31),
    min_opportunity: float | None = Query(None, ge=0, le=10),
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[WeeklyRetrospectiveData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = generate_weekly_retrospective(
        db,
        days=days,
        min_opportunity=min_opportunity,
        workspace_id=x_workspace_id,
    )
    return ApiResponse(success=True, data=data, error=None)
