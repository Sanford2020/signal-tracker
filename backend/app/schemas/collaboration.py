from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IntelFileCollaborationRead(BaseModel):
    intel_file_id: UUID
    owner_user_id: UUID | None
    review_note: str | None
    last_reviewed_at: datetime | None


class IntelFileCollaborationUpdateRequest(BaseModel):
    owner_user_id: UUID | None = None
    review_note: str | None = Field(None, max_length=2000)
    mark_reviewed: bool = False


class IntelFileCollaborationData(BaseModel):
    item: IntelFileCollaborationRead


class IntelFileCommentCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class IntelFileCommentRead(BaseModel):
    id: UUID
    intel_file_id: UUID
    author_user_id: UUID
    author_email: str
    author_name: str
    body: str
    created_at: datetime


class IntelFileCommentListData(BaseModel):
    items: list[IntelFileCommentRead]
    total: int


class IntelFileCommentCreateData(BaseModel):
    item: IntelFileCommentRead


class IntelFileCommentModelRead(BaseModel):
    id: UUID
    intel_file_id: UUID
    author_user_id: UUID
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
