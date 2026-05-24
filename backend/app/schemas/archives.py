from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LifecycleStatus


class TrendArchiveSnapshotRead(BaseModel):
    id: UUID
    intel_file_id: UUID
    archive_date: date
    status: LifecycleStatus
    heat_score: float | None
    credibility_score: float | None
    opportunity_score: float | None
    risk_score: float | None
    evidence_count: int
    source_count: int
    last_seen_at: datetime
    captured_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrendArchiveRunRequest(BaseModel):
    archive_date: date | None = None
    limit: int = Field(500, ge=1, le=5000)


class TrendArchiveRunData(BaseModel):
    archive_date: date
    checked_count: int
    created_count: int
    updated_count: int
    items: list[TrendArchiveSnapshotRead]


class TrendArchiveListData(BaseModel):
    items: list[TrendArchiveSnapshotRead]
    total: int
