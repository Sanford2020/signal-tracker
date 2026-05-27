from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IntelFileSavedViewFilters(BaseModel):
    query: str = Field("", max_length=200)
    status: str = Field("", max_length=64)
    sort: str = Field(
        "updated_at",
        pattern="^(updated_at|last_seen_at|first_seen_at|opportunity_score|heat_score|risk_score|evidence_count)$",
    )
    order: str = Field("desc", pattern="^(asc|desc)$")
    page_size: int = Field(20, ge=1, le=100)


class IntelFileSavedViewCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    filters: IntelFileSavedViewFilters
    is_default: bool = False


class IntelFileSavedViewUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    filters: IntelFileSavedViewFilters | None = None
    is_default: bool | None = None


class IntelFileSavedViewRead(BaseModel):
    id: UUID
    workspace_id: UUID | None
    name: str
    slug: str
    filters: IntelFileSavedViewFilters
    is_default: bool
    created_by_email: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntelFileSavedViewListData(BaseModel):
    items: list[IntelFileSavedViewRead]
    total: int


class IntelFileSavedViewData(BaseModel):
    item: IntelFileSavedViewRead


class IntelFileSavedViewDeleteData(BaseModel):
    deleted_id: UUID
