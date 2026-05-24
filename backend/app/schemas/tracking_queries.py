from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TrackingQueryRead(BaseModel):
    id: UUID
    intel_file_id: UUID
    query: str
    normalized_query: str
    source_hint: str | None
    rationale: str | None
    enabled: bool
    meta: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrackingQueryGenerateRequest(BaseModel):
    limit: int = 12
    regenerate: bool = False


class TrackingQueryGenerateData(BaseModel):
    items: list[TrackingQueryRead]
    created_count: int
