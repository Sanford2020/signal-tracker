from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UsageTotals(BaseModel):
    ai_extraction: int = 0
    source_check: int = 0


class UsageLimits(BaseModel):
    ai_extraction: int
    source_check: int


class UsageSummaryData(BaseModel):
    workspace_id: UUID | None
    month_start: datetime
    totals: UsageTotals
    limits: UsageLimits
