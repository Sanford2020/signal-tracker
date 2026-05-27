from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SourceCheckRunRequest(BaseModel):
    limit: int = Field(20, ge=1, le=100)


class SourceCheckResultRead(BaseModel):
    id: UUID
    run_id: UUID
    tracking_query_id: UUID
    title: str
    url: str | None
    snippet: str | None
    source_name: str | None
    source_hint: str | None
    raw: dict[str, Any] | None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceCheckRunRead(BaseModel):
    id: UUID
    workspace_id: UUID | None
    status: str
    checked_query_count: int
    result_count: int
    error: str | None
    started_at: datetime
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class SourceCheckRunData(BaseModel):
    run: SourceCheckRunRead
    results: list[SourceCheckResultRead]


class SourceCheckRunListData(BaseModel):
    items: list[SourceCheckRunRead]
    total: int


class SourceProviderHealthErrorRead(BaseModel):
    tracking_query_id: UUID
    query: str
    error: str


class SourceProviderHealthRead(BaseModel):
    source_hint: str
    enabled_query_count: int
    recent_result_count: int
    last_result_at: datetime | None
    recent_error_count: int
    latest_error: str | None
    recent_errors: list[SourceProviderHealthErrorRead] = Field(default_factory=list)
    latest_run_status: str | None
    latest_run_error: str | None


class SourceProviderHealthData(BaseModel):
    items: list[SourceProviderHealthRead]
    total: int
