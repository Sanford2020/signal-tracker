from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import LifecycleStatus


class BriefingScores(BaseModel):
    heat: float | None
    credibility: float | None
    opportunity: float | None
    risk: float | None


class BriefingEvidence(BaseModel):
    raw_item_id: UUID
    title: str
    url: str | None


class BriefingItem(BaseModel):
    intel_file_id: UUID
    title: str
    status: LifecycleStatus
    reason: str
    scores: BriefingScores
    key_evidence: list[BriefingEvidence] = Field(default_factory=list)


class BriefingMeta(BaseModel):
    generated_at: datetime
    window_hours: int
    item_count: int


class BriefingSections(BaseModel):
    new_files: list[BriefingItem] = Field(default_factory=list)
    updated_files: list[BriefingItem] = Field(default_factory=list)
    resurrected: list[BriefingItem] = Field(default_factory=list)
    high_opportunity: list[BriefingItem] = Field(default_factory=list)
    risk_or_noise: list[BriefingItem] = Field(default_factory=list)


class DailyBriefingData(BaseModel):
    meta: BriefingMeta
    overview: str
    sections: BriefingSections
    debug: dict[str, Any] = Field(default_factory=dict)


class WeeklyBriefingMeta(BaseModel):
    generated_at: datetime
    window_days: int
    item_count: int


class WeeklyBriefingSections(BaseModel):
    changed_files: list[BriefingItem] = Field(default_factory=list)
    resurrected: list[BriefingItem] = Field(default_factory=list)
    verified_or_debunked: list[BriefingItem] = Field(default_factory=list)
    opportunity_gainers: list[BriefingItem] = Field(default_factory=list)
    cooling_or_noise: list[BriefingItem] = Field(default_factory=list)


class WeeklyRetrospectiveData(BaseModel):
    meta: WeeklyBriefingMeta
    overview: str
    sections: WeeklyBriefingSections
    debug: dict[str, Any] = Field(default_factory=dict)
