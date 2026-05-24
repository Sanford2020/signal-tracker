import re
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Evidence, IntelFile, MatchSuggestion, RawItem, Source, SourceCheckResult, SourceCheckRun, SourceType, TrackingQuery
from app.models.enums import AttachedBy, EvidenceType
from app.modules.inbox.service import compute_content_hash, resolve_title
from app.modules.intel_files.service import attach_evidence
from app.schemas.match_suggestions import (
    MatchSuggestionAcceptData,
    MatchSuggestionAcceptRequest,
    MatchSuggestionGenerateData,
    MatchSuggestionGenerateRequest,
    MatchSuggestionListData,
    MatchSuggestionRead,
    MatchSuggestionStatusUpdateData,
    MatchSuggestionStatusUpdateRequest,
)
from app.schemas.intel_files import EvidenceAttachRequest

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+_.-]{2,}", re.IGNORECASE)
_STOPWORDS = {
    "and",
    "for",
    "from",
    "with",
    "the",
    "this",
    "that",
    "into",
    "about",
    "role",
    "team",
    "lead",
    "news",
    "update",
}


def _tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return {token.lower() for token in _TOKEN_RE.findall(value) if token.lower() not in _STOPWORDS}


def _entity_terms(entities: list) -> set[str]:
    terms: set[str] = set()
    for entity in entities:
        if isinstance(entity, dict):
            terms.update(_tokens(str(entity.get("name") or "")))
        else:
            terms.update(_tokens(str(entity)))
    return terms


def _file_terms(intel_file: IntelFile, query: TrackingQuery) -> set[str]:
    terms = _tokens(intel_file.title)
    terms.update(_tokens(intel_file.thesis))
    terms.update(_tokens(query.query))
    for keyword in intel_file.keywords:
        terms.update(_tokens(str(keyword)))
    terms.update(_entity_terms(intel_file.entities))
    return terms


def _result_terms(result: SourceCheckResult) -> set[str]:
    terms = _tokens(result.title)
    terms.update(_tokens(result.snippet))
    terms.update(_tokens(result.url))
    return terms


def _score_match(intel_file: IntelFile, query: TrackingQuery, result: SourceCheckResult) -> tuple[float, str]:
    file_terms = _file_terms(intel_file, query)
    result_terms = _result_terms(result)
    if not file_terms or not result_terms:
        return 0.0, "No comparable terms."

    overlap = sorted(file_terms & result_terms)
    if not overlap:
        return 0.0, "No shared file/result terms."

    coverage = len(overlap) / min(len(file_terms), 8)
    confidence = min(0.95, 0.45 + coverage)
    rationale = f"Matched terms: {', '.join(overlap[:8])}."
    return round(confidence, 2), rationale


def _to_read(suggestion: MatchSuggestion, result: SourceCheckResult) -> MatchSuggestionRead:
    return MatchSuggestionRead(
        id=suggestion.id,
        intel_file_id=suggestion.intel_file_id,
        source_check_result_id=suggestion.source_check_result_id,
        suggested_evidence_type=suggestion.suggested_evidence_type,
        confidence=suggestion.confidence,
        rationale=suggestion.rationale,
        status=suggestion.status,
        created_at=suggestion.created_at,
        decided_at=suggestion.decided_at,
        result_title=result.title,
        result_url=result.url,
        result_snippet=result.snippet,
        source_name=result.source_name,
    )


def generate_match_suggestions_for_run(
    db: Session,
    run_id: UUID,
    payload: MatchSuggestionGenerateRequest,
) -> MatchSuggestionGenerateData:
    run = db.scalar(select(SourceCheckRun).where(SourceCheckRun.id == run_id))
    if run is None:
        raise ValueError("Source check run not found.")

    results = db.scalars(
        select(SourceCheckResult)
        .options(
            selectinload(SourceCheckResult.tracking_query).selectinload(TrackingQuery.intel_file),
        )
        .where(SourceCheckResult.run_id == run_id)
        .order_by(SourceCheckResult.checked_at.asc(), SourceCheckResult.id.asc())
    ).all()

    created: list[tuple[MatchSuggestion, SourceCheckResult]] = []
    for result in results:
        query = result.tracking_query
        intel_file = query.intel_file
        confidence, rationale = _score_match(intel_file, query, result)
        if confidence < payload.min_confidence:
            continue

        existing = db.scalar(
            select(MatchSuggestion).where(
                MatchSuggestion.intel_file_id == intel_file.id,
                MatchSuggestion.source_check_result_id == result.id,
            )
        )
        if existing is not None:
            continue

        suggestion = MatchSuggestion(
            intel_file_id=intel_file.id,
            source_check_result_id=result.id,
            suggested_evidence_type="follow_up",
            confidence=confidence,
            rationale=rationale,
            status="open",
        )
        db.add(suggestion)
        db.flush()
        created.append((suggestion, result))

    db.commit()
    for suggestion, _ in created:
        db.refresh(suggestion)

    return MatchSuggestionGenerateData(
        items=[_to_read(suggestion, result) for suggestion, result in created],
        created_count=len(created),
    )


def list_match_suggestions(
    db: Session,
    intel_file_id: UUID,
    *,
    status: str | None = "open",
) -> MatchSuggestionListData:
    intel_file = db.scalar(select(IntelFile).where(IntelFile.id == intel_file_id))
    if intel_file is None:
        raise ValueError("Intel file not found.")

    query = (
        select(MatchSuggestion, SourceCheckResult)
        .join(SourceCheckResult, SourceCheckResult.id == MatchSuggestion.source_check_result_id)
        .where(MatchSuggestion.intel_file_id == intel_file_id)
        .order_by(MatchSuggestion.created_at.desc(), MatchSuggestion.id.desc())
    )
    if status is not None:
        query = query.where(MatchSuggestion.status == status)

    rows = db.execute(query).all()
    items = [_to_read(suggestion, result) for suggestion, result in rows]
    return MatchSuggestionListData(items=items, total=len(items))


def update_match_suggestion_status(
    db: Session,
    suggestion_id: UUID,
    payload: MatchSuggestionStatusUpdateRequest,
) -> MatchSuggestionStatusUpdateData:
    row = db.execute(
        select(MatchSuggestion, SourceCheckResult)
        .join(SourceCheckResult, SourceCheckResult.id == MatchSuggestion.source_check_result_id)
        .where(MatchSuggestion.id == suggestion_id)
    ).first()
    if row is None:
        raise ValueError("Match suggestion not found.")

    suggestion, result = row
    suggestion.status = payload.status
    suggestion.decided_at = datetime.now(UTC) if payload.status != "open" else None
    db.commit()
    db.refresh(suggestion)
    return MatchSuggestionStatusUpdateData(item=_to_read(suggestion, result))


def _get_or_create_source_check_source(db: Session, result: SourceCheckResult) -> Source:
    name = result.source_name or "Source Check Results"
    source = db.scalar(
        select(Source).where(
            Source.name == name,
            Source.source_type == SourceType.SEARCH,
        )
    )
    if source is not None:
        return source

    source = Source(
        name=name,
        source_type=SourceType.SEARCH,
        url=result.url,
        category=result.source_hint,
        trust_tier=2,
        enabled=True,
        license_notes="Created from accepted source check result.",
    )
    db.add(source)
    db.flush()
    return source


def _raw_item_from_result(db: Session, result: SourceCheckResult) -> tuple[RawItem, bool]:
    content = result.snippet or result.title
    content_hash = compute_content_hash(result.url, content, result.title)
    existing = db.scalar(select(RawItem).where(RawItem.content_hash == content_hash))
    if existing is not None:
        return existing, True

    source = _get_or_create_source_check_source(db, result)
    raw_item = RawItem(
        source_id=source.id,
        title=resolve_title(result.url, result.title, content),
        url=result.url,
        content=content,
        content_hash=content_hash,
        captured_at=result.checked_at,
        raw_json={
            "source_check_result_id": str(result.id),
            "source_check_run_id": str(result.run_id),
            "source_hint": result.source_hint,
            "raw": result.raw,
        },
    )
    db.add(raw_item)
    db.flush()
    return raw_item, False


def accept_match_suggestion(
    db: Session,
    suggestion_id: UUID,
    payload: MatchSuggestionAcceptRequest,
) -> MatchSuggestionAcceptData:
    row = db.execute(
        select(MatchSuggestion, SourceCheckResult)
        .join(SourceCheckResult, SourceCheckResult.id == MatchSuggestion.source_check_result_id)
        .where(MatchSuggestion.id == suggestion_id)
    ).first()
    if row is None:
        raise ValueError("Match suggestion not found.")

    suggestion, result = row
    raw_item, duplicate = _raw_item_from_result(db, result)
    existing_evidence = db.scalar(
        select(Evidence).where(
            Evidence.intel_file_id == suggestion.intel_file_id,
            Evidence.raw_item_id == raw_item.id,
        )
    )
    if existing_evidence is None:
        evidence, _ = attach_evidence(
            db,
            suggestion.intel_file_id,
            EvidenceAttachRequest(
                raw_item_id=raw_item.id,
                evidence_type=EvidenceType.FOLLOW_UP,
                confidence=suggestion.confidence,
                attached_by=AttachedBy.USER,
                rationale=payload.rationale or suggestion.rationale,
            ),
        )
    else:
        evidence = existing_evidence

    suggestion.status = "accepted"
    suggestion.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(suggestion)

    return MatchSuggestionAcceptData(
        item=_to_read(suggestion, result),
        raw_item_id=raw_item.id,
        evidence_id=evidence.id,
        duplicate_raw_item=duplicate,
    )
