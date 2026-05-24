from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import RawItem, SignalAnalysis
from app.modules.extraction.client import get_extractor
from app.modules.extraction.normalize import ExtractionError, normalize_signal_type
from app.modules.extraction.schemas import ExtractionInput, ExtractionSourceContext, PROMPT_VERSION
from app.modules.usage.service import AI_EXTRACTION, assert_usage_available, record_usage


def build_extraction_input(raw_item: RawItem) -> ExtractionInput:
    source = raw_item.source
    return ExtractionInput(
        title=raw_item.title,
        url=raw_item.url,
        content=raw_item.content,
        source=ExtractionSourceContext(
            name=source.name,
            source_type=source.source_type.value,
            trust_tier=source.trust_tier,
        ),
        captured_at=raw_item.captured_at,
    )


def to_analysis_read_dict(analysis: SignalAnalysis) -> dict:
    return {
        "id": analysis.id,
        "raw_item_id": analysis.raw_item_id,
        "summary": analysis.summary,
        "signal_type": analysis.signal_type.value,
        "entities": analysis.entities,
        "keywords": analysis.keywords,
        "claims": analysis.claims,
        "suggested_tracking_queries": analysis.suggested_tracking_queries,
        "novelty_score": analysis.novelty_score,
        "relevance_score": analysis.relevance_score,
        "credibility_hint": analysis.credibility_hint,
        "risk_hint": analysis.risk_hint,
        "opportunity_types": analysis.opportunity_types,
        "rationale": analysis.rationale,
        "language": analysis.language,
        "model": analysis.model,
        "prompt_version": analysis.prompt_version,
        "created_at": analysis.created_at,
    }


def analyze_raw_item(
    db: Session,
    raw_item_id: UUID,
    *,
    workspace_id: UUID | None = None,
) -> SignalAnalysis:
    raw_item = db.scalar(
        select(RawItem)
        .options(selectinload(RawItem.source), selectinload(RawItem.signal_analysis))
        .where(RawItem.id == raw_item_id)
    )
    if raw_item is None or (workspace_id is not None and raw_item.workspace_id != workspace_id):
        raise ValueError("Raw item not found.")

    if raw_item.signal_analysis is not None:
        return raw_item.signal_analysis

    assert_usage_available(
        db,
        workspace_id=raw_item.workspace_id,
        usage_type=AI_EXTRACTION,
        amount=1,
    )

    settings = get_settings()
    extractor = get_extractor(settings)
    input_data = build_extraction_input(raw_item)

    try:
        output, raw_output = extractor.extract(input_data)
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"Extraction failed: {exc}") from exc

    analysis = SignalAnalysis(
        raw_item_id=raw_item.id,
        summary=output.summary,
        signal_type=normalize_signal_type(output.signal_type),
        entities=output.entities,
        keywords=output.keywords,
        claims=output.claims,
        suggested_tracking_queries=output.suggested_tracking_queries,
        opportunity_types=output.opportunity_types,
        novelty_score=output.novelty_score,
        relevance_score=output.relevance_score,
        credibility_hint=output.credibility_hint,
        risk_hint=output.risk_hint,
        rationale=output.rationale,
        language=output.language,
        model=extractor.model_name,
        prompt_version=PROMPT_VERSION,
        raw_output=raw_output,
    )
    db.add(analysis)
    record_usage(
        db,
        workspace_id=raw_item.workspace_id,
        usage_type=AI_EXTRACTION,
        amount=1,
        meta={"raw_item_id": str(raw_item.id)},
    )
    db.commit()
    db.refresh(analysis)

    return analysis
