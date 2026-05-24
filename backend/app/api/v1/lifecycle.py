from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.lifecycle.worker import run_lifecycle_worker
from app.schemas.api import ApiResponse
from app.schemas.lifecycle_worker import LifecycleWorkerRunData, LifecycleWorkerRunRequest

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])


@router.post("/run", response_model=ApiResponse[LifecycleWorkerRunData])
def run_lifecycle_worker_route(
    payload: LifecycleWorkerRunRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[LifecycleWorkerRunData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    scoped_payload = payload.model_copy(update={"workspace_id": x_workspace_id})
    data = run_lifecycle_worker(db, scoped_payload)
    return ApiResponse(success=True, data=data, error=None)
