from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.archives.service import run_trend_archive_snapshots
from app.schemas.api import ApiResponse
from app.schemas.archives import TrendArchiveRunData, TrendArchiveRunRequest

router = APIRouter(prefix="/archives", tags=["archives"])


@router.post("/snapshots/run", response_model=ApiResponse[TrendArchiveRunData])
def run_trend_archive_snapshots_route(
    payload: TrendArchiveRunRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[TrendArchiveRunData]:
    data = run_trend_archive_snapshots(db, payload)
    return ApiResponse(success=True, data=data, error=None)
