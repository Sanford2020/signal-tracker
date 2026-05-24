from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import LifecycleStatus


class LifecycleWorkerRunRequest(BaseModel):
    now: datetime | None = None
    limit: int = Field(50, ge=1, le=500)
    reason: str = "lifecycle worker"
    workspace_id: UUID | None = None


class LifecycleWorkerTransition(BaseModel):
    intel_file_id: UUID
    previous_status: LifecycleStatus
    next_status: LifecycleStatus
    reason: str


class LifecycleWorkerRunData(BaseModel):
    checked_count: int
    transitioned_count: int
    items: list[LifecycleWorkerTransition]
