from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import LifecycleStatus


class LifecycleEvaluateRequest(BaseModel):
    reason: str = "manual"
    now: datetime | None = None


class LifecycleEvaluateData(BaseModel):
    previous_status: LifecycleStatus
    next_status: LifecycleStatus
    reason: str
    evidence_ids: list[UUID] = Field(default_factory=list)
    score_changes: dict[str, list[float | None]]


class LifecycleStatusOverrideRequest(BaseModel):
    status: LifecycleStatus
    reason: str = Field(min_length=3, max_length=1000)
    now: datetime | None = None


class LifecycleStatusOverrideData(BaseModel):
    previous_status: LifecycleStatus
    next_status: LifecycleStatus
    reason: str
