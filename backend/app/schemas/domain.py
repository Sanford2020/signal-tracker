from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AlertChannel,
    AlertSeverity,
    AlertStatus,
    AlertType,
    AttachedBy,
    EvidenceType,
    IntelEventType,
    LifecycleStatus,
    SignalType,
    SourceType,
)


def clamp_score(value: float | None) -> float | None:
    if value is None:
        return None
    return max(0.0, min(10.0, value))


class SourceCreate(BaseModel):
    name: str
    source_type: SourceType
    url: str | None = None
    category: str | None = None
    trust_tier: int = Field(default=2, ge=0, le=3)
    fetch_interval_minutes: int | None = None
    enabled: bool = True
    license_notes: str | None = None


class SourceRead(SourceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class RawItemCreate(BaseModel):
    source_id: UUID
    title: str
    url: str | None = None
    content: str | None = None
    content_hash: str
    published_at: datetime | None = None
    raw_json: dict[str, Any] | None = None


class RawItemRead(RawItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    captured_at: datetime


class SignalAnalysisCreate(BaseModel):
    raw_item_id: UUID
    summary: str
    signal_type: SignalType
    entities: list[Any] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    claims: list[Any] = Field(default_factory=list)
    suggested_tracking_queries: list[str] = Field(default_factory=list)
    opportunity_types: list[str] = Field(default_factory=list)
    novelty_score: float | None = None
    relevance_score: float | None = None
    credibility_hint: float | None = None
    risk_hint: float | None = None
    rationale: str | None = None
    language: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    raw_output: dict[str, Any] | None = None

    @field_validator(
        "novelty_score",
        "relevance_score",
        "credibility_hint",
        "risk_hint",
    )
    @classmethod
    def validate_scores(cls, value: float | None) -> float | None:
        return clamp_score(value)


class SignalAnalysisRead(SignalAnalysisCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class IntelFileCreate(BaseModel):
    title: str
    thesis: str | None = None
    status: LifecycleStatus = LifecycleStatus.NEW
    first_seen_at: datetime
    last_seen_at: datetime
    primary_signal_type: SignalType | None = None
    entities: list[Any] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    source_count: int = 0
    evidence_count: int = 0
    heat_score: float | None = None
    credibility_score: float | None = None
    opportunity_score: float | None = None
    risk_score: float | None = None
    owner_notes: str | None = None

    @field_validator("heat_score", "credibility_score", "opportunity_score", "risk_score")
    @classmethod
    def validate_scores(cls, value: float | None) -> float | None:
        return clamp_score(value)


class IntelFileRead(IntelFileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class EvidenceCreate(BaseModel):
    intel_file_id: UUID
    raw_item_id: UUID
    evidence_type: EvidenceType
    confidence: float | None = None
    attached_by: AttachedBy = AttachedBy.SYSTEM
    rationale: str | None = None

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float | None) -> float | None:
        return clamp_score(value)


class EvidenceRead(EvidenceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attached_at: datetime


class IntelEventCreate(BaseModel):
    intel_file_id: UUID
    event_type: IntelEventType
    title: str
    description: str | None = None
    event_time: datetime | None = None
    source_evidence_id: UUID | None = None
    metadata: dict[str, Any] | None = None


class IntelEventRead(IntelEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_time: datetime


class LifecycleSnapshotCreate(BaseModel):
    intel_file_id: UUID
    status: LifecycleStatus
    heat_score: float | None = None
    credibility_score: float | None = None
    opportunity_score: float | None = None
    risk_score: float | None = None
    reason: str | None = None
    snapshot_time: datetime | None = None

    @field_validator("heat_score", "credibility_score", "opportunity_score", "risk_score")
    @classmethod
    def validate_scores(cls, value: float | None) -> float | None:
        return clamp_score(value)


class LifecycleSnapshotRead(LifecycleSnapshotCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    snapshot_time: datetime


class AlertEventCreate(BaseModel):
    intel_file_id: UUID
    alert_type: AlertType
    message: str
    severity: AlertSeverity = AlertSeverity.WATCH
    status: AlertStatus = AlertStatus.PENDING
    channel: AlertChannel = AlertChannel.IN_APP


class AlertEventRead(AlertEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
