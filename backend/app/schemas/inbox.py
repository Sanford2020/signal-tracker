from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class InboxSubmitRequest(BaseModel):
    url: str | None = None
    title: str | None = None
    content: str | None = None
    source_id: UUID | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "InboxSubmitRequest":
        if not any(
            value and str(value).strip()
            for value in (self.url, self.title, self.content)
        ):
            raise ValueError("At least one of url, title, or content is required.")
        return self


class InboxRawItem(BaseModel):
    id: UUID
    workspace_id: UUID | None
    title: str
    url: str | None
    content: str | None
    source_id: UUID
    content_hash: str
    published_at: datetime | None
    captured_at: datetime


class InboxSubmitData(BaseModel):
    raw_item: InboxRawItem
    duplicate: bool = False


class InboxListItem(BaseModel):
    raw_item: InboxRawItem
    analysis_status: Literal["pending", "complete"]
    has_intel_file: bool = False


class InboxListData(BaseModel):
    items: list[InboxListItem]
    total: int
    page: int
    page_size: int = Field(default=20)
