from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.lifecycle.worker import run_lifecycle_worker
from app.schemas.api import ApiResponse
from app.schemas.lifecycle_worker import LifecycleWorkerRunData, LifecycleWorkerRunRequest

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])


@router.post("/run", response_model=ApiResponse[LifecycleWorkerRunData])
def run_lifecycle_worker_route(
    payload: LifecycleWorkerRunRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[LifecycleWorkerRunData]:
    data = run_lifecycle_worker(db, payload)
    return ApiResponse(success=True, data=data, error=None)
