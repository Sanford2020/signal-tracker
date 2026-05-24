from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.domain import clamp_score


PROMPT_VERSION = "signal_extract_v1"


class ExtractionSourceContext(BaseModel):
    name: str
    source_type: str
    trust_tier: int


class ExtractionInput(BaseModel):
    title: str
    url: str | None = None
    content: str | None = None
    source: ExtractionSourceContext
    captured_at: datetime


class ExtractionOutput(BaseModel):
    summary: str
    signal_type: str
    entities: list[dict[str, Any]] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    claims: list[dict[str, Any]] = Field(default_factory=list)
    suggested_tracking_queries: list[str] = Field(default_factory=list)
    novelty_score: float | None = None
    relevance_score: float | None = None
    credibility_hint: float | None = None
    risk_hint: float | None = None
    opportunity_types: list[str] = Field(default_factory=list)
    rationale: str | None = None
    language: str | None = "en"

    @field_validator(
        "novelty_score",
        "relevance_score",
        "credibility_hint",
        "risk_hint",
    )
    @classmethod
    def validate_scores(cls, value: float | None) -> float | None:
        return clamp_score(value)
