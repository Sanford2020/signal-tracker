from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BootstrapRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    workspace_name: str = Field(min_length=1, max_length=255)


class UserRead(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceRead(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMembershipRead(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberRead(BaseModel):
    membership_id: UUID
    user_id: UUID
    email: str
    name: str
    role: str
    joined_at: datetime


class WorkspaceMemberCreateRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    role: str = Field(default="member", pattern="^(admin|member)$")


class BootstrapData(BaseModel):
    user: UserRead
    workspace: WorkspaceRead
    membership: WorkspaceMembershipRead
    access_token: str


class WorkspaceListData(BaseModel):
    items: list[WorkspaceRead]
    total: int


class WorkspaceMemberListData(BaseModel):
    items: list[WorkspaceMemberRead]
    total: int


class WorkspaceMemberCreateData(BaseModel):
    member: WorkspaceMemberRead
    access_token: str
