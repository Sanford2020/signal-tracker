from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ScoreUpdateRequest(BaseModel):
    reason: str = "manual"


class ScoreUpdateData(BaseModel):
    novelty_score: float
    heat_score: float
    credibility_score: float
    opportunity_score: float
    risk_score: float
    score_changes: dict[str, list[float | None]]
    rationale: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    snapshot_time: datetime
