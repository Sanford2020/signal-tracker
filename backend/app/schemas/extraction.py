from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnalysisData(BaseModel):
    id: UUID
    raw_item_id: UUID
    summary: str
    signal_type: str
    entities: list[Any]
    keywords: list[str]
    claims: list[Any]
    suggested_tracking_queries: list[str]
    novelty_score: float | None
    relevance_score: float | None
    credibility_hint: float | None
    risk_hint: float | None
    opportunity_types: list[str]
    rationale: str | None
    language: str | None
    model: str | None
    prompt_version: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyzeResponseData(BaseModel):
    analysis: AnalysisData
