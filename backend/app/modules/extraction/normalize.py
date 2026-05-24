from typing import Any

from app.models.enums import SignalType
from app.modules.extraction.schemas import ExtractionOutput

SIGNAL_TYPE_ALIASES = {
    "hiring": SignalType.HIRING,
    "product": SignalType.PRODUCT,
    "github": SignalType.GITHUB,
    "funding": SignalType.FUNDING,
    "policy": SignalType.POLICY,
    "research": SignalType.RESEARCH,
    "market": SignalType.MARKET,
    "rumor": SignalType.RUMOR,
    "incident": SignalType.OTHER,
    "community": SignalType.OTHER,
    "partnership": SignalType.OTHER,
    "other": SignalType.OTHER,
}


class ExtractionError(Exception):
    def __init__(self, message: str, raw_output: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.raw_output = raw_output


def normalize_signal_type(value: str | None) -> SignalType:
    if not value:
        return SignalType.OTHER
    key = value.strip().lower()
    return SIGNAL_TYPE_ALIASES.get(key, SignalType.OTHER)


def ensure_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_extraction_output(data: dict[str, Any]) -> ExtractionOutput:
    summary = str(data.get("summary", "")).strip()
    if not summary:
        raise ExtractionError("Extraction summary must not be empty.", raw_output=data)

    normalized = {
        "summary": summary,
        "signal_type": str(data.get("signal_type", "other")),
        "entities": ensure_list(data.get("entities")),
        "keywords": [str(k) for k in ensure_list(data.get("keywords"))],
        "claims": ensure_list(data.get("claims")),
        "suggested_tracking_queries": [
            str(q) for q in ensure_list(data.get("suggested_tracking_queries"))
        ],
        "novelty_score": data.get("novelty_score"),
        "relevance_score": data.get("relevance_score"),
        "credibility_hint": data.get("credibility_hint"),
        "risk_hint": data.get("risk_hint"),
        "opportunity_types": [str(o) for o in ensure_list(data.get("opportunity_types"))],
        "rationale": data.get("rationale"),
        "language": data.get("language") or "en",
    }
    return ExtractionOutput.model_validate(normalized)
