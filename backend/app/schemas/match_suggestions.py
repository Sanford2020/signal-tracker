from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MatchSuggestionGenerateRequest(BaseModel):
    min_confidence: float = Field(0.65, ge=0, le=1)


class MatchSuggestionRead(BaseModel):
    id: UUID
    intel_file_id: UUID
    source_check_result_id: UUID
    suggested_evidence_type: str
    confidence: float
    rationale: str
    status: str
    created_at: datetime
    decided_at: datetime | None
    result_title: str
    result_url: str | None
    result_snippet: str | None
    source_name: str | None


class MatchSuggestionGenerateData(BaseModel):
    items: list[MatchSuggestionRead]
    created_count: int


class MatchSuggestionListData(BaseModel):
    items: list[MatchSuggestionRead]
    total: int


class MatchSuggestionStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(open|accepted|dismissed)$")


class MatchSuggestionStatusUpdateData(BaseModel):
    item: MatchSuggestionRead


class MatchSuggestionModelRead(BaseModel):
    id: UUID
    intel_file_id: UUID
    source_check_result_id: UUID
    suggested_evidence_type: str
    confidence: float
    rationale: str
    status: str
    created_at: datetime
    decided_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class MatchSuggestionAcceptRequest(BaseModel):
    rationale: str | None = None


class MatchSuggestionAcceptData(BaseModel):
    item: MatchSuggestionRead
    raw_item_id: UUID
    evidence_id: UUID
    duplicate_raw_item: bool
