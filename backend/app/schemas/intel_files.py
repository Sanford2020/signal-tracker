from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AttachedBy, EvidenceType, IntelEventType, LifecycleStatus, SignalType


class IntelFileCreateRequest(BaseModel):
    raw_item_id: UUID
    analysis_id: UUID | None = None
    title: str | None = None
    thesis: str | None = None


class IntelFileSummary(BaseModel):
    id: UUID
    workspace_id: UUID | None
    owner_user_id: UUID | None
    title: str
    thesis: str | None
    status: LifecycleStatus
    first_seen_at: datetime
    last_seen_at: datetime
    primary_signal_type: SignalType | None
    entities: list[Any] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    source_count: int
    evidence_count: int
    heat_score: float | None
    credibility_score: float | None
    opportunity_score: float | None
    risk_score: float | None
    review_note: str | None
    last_reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntelFileCreateData(BaseModel):
    intel_file: IntelFileSummary


class IntelFileListData(BaseModel):
    items: list[IntelFileSummary]
    total: int
    page: int
    page_size: int


class EvidenceAttachRequest(BaseModel):
    raw_item_id: UUID
    evidence_type: EvidenceType = EvidenceType.FOLLOW_UP
    confidence: float | None = None
    attached_by: AttachedBy = AttachedBy.USER
    rationale: str | None = None


class EvidenceSummary(BaseModel):
    id: UUID
    intel_file_id: UUID
    raw_item_id: UUID
    evidence_type: EvidenceType
    confidence: float | None
    attached_by: AttachedBy
    rationale: str | None
    attached_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceAttachData(BaseModel):
    evidence: EvidenceSummary
    intel_file: IntelFileSummary


class IntelEventSummary(BaseModel):
    id: UUID
    intel_file_id: UUID
    event_type: IntelEventType
    event_time: datetime
    title: str
    description: str | None
    source_evidence_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


class IntelFileDetailData(BaseModel):
    intel_file: IntelFileSummary
    novelty_score: float | None
    evidence: list[EvidenceSummary]
    timeline: list[IntelEventSummary]
    snapshots: list[Any] = Field(default_factory=list)
    alerts: list[Any] = Field(default_factory=list)
