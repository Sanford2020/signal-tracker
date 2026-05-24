from uuid import UUID

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Evidence, IntelEvent, IntelFile, RawItem, SignalAnalysis
from app.models.enums import AttachedBy, EvidenceType, IntelEventType, LifecycleStatus
from app.schemas.intel_files import (
    EvidenceAttachRequest,
    EvidenceSummary,
    IntelEventSummary,
    IntelFileCreateRequest,
    IntelFileDetailData,
    IntelFileListData,
    IntelFileSummary,
)


class IntelFileError(Exception):
    pass


class EvidenceConflictError(Exception):
    pass


def _initial_opportunity_score(analysis: SignalAnalysis) -> float | None:
    if analysis.relevance_score is not None and analysis.novelty_score is not None:
        return round((analysis.relevance_score + analysis.novelty_score) / 2, 1)
    if analysis.relevance_score is not None:
        return analysis.relevance_score
    if analysis.novelty_score is not None:
        return analysis.novelty_score
    return None


def _resolve_seen_at(raw_item: RawItem):
    return raw_item.published_at or raw_item.captured_at


def _refresh_source_count(db: Session, intel_file: IntelFile) -> None:
    source_ids = db.scalars(
        select(RawItem.source_id)
        .join(Evidence, Evidence.raw_item_id == RawItem.id)
        .where(Evidence.intel_file_id == intel_file.id)
    ).all()
    intel_file.source_count = len(set(source_ids))


def attach_evidence(
    db: Session,
    intel_file_id: UUID,
    payload: EvidenceAttachRequest,
    *,
    workspace_id: UUID | None = None,
) -> tuple[Evidence, IntelFile]:
    intel_file = db.scalar(select(IntelFile).where(IntelFile.id == intel_file_id))
    if intel_file is None:
        raise ValueError("Intel file not found.")
    if workspace_id is not None and intel_file.workspace_id != workspace_id:
        raise ValueError("Intel file not found.")

    raw_item = db.scalar(select(RawItem).where(RawItem.id == payload.raw_item_id))
    if raw_item is None:
        raise ValueError("Raw item not found.")
    if workspace_id is not None and raw_item.workspace_id != workspace_id:
        raise ValueError("Raw item not found.")

    existing = db.scalar(
        select(Evidence).where(
            Evidence.intel_file_id == intel_file_id,
            Evidence.raw_item_id == payload.raw_item_id,
        )
    )
    if existing is not None:
        raise EvidenceConflictError("Evidence for this raw item is already attached to the file.")

    evidence = Evidence(
        intel_file_id=intel_file_id,
        raw_item_id=payload.raw_item_id,
        evidence_type=payload.evidence_type,
        confidence=payload.confidence,
        attached_by=payload.attached_by,
        rationale=payload.rationale,
    )
    db.add(evidence)
    db.flush()

    seen_at = _resolve_seen_at(raw_item)
    event = IntelEvent(
        intel_file_id=intel_file_id,
        event_type=IntelEventType.EVIDENCE_ADDED,
        event_time=seen_at,
        title="Evidence added",
        description=payload.rationale or f"Attached raw item: {raw_item.title}",
        source_evidence_id=evidence.id,
        metadata_={
            "raw_item_id": str(raw_item.id),
            "evidence_type": payload.evidence_type.value,
        },
    )
    db.add(event)

    intel_file.evidence_count += 1
    _refresh_source_count(db, intel_file)
    if seen_at > intel_file.last_seen_at:
        intel_file.last_seen_at = seen_at

    db.commit()
    db.refresh(evidence)
    db.refresh(intel_file)
    return evidence, intel_file


def to_intel_file_summary(intel_file: IntelFile) -> IntelFileSummary:
    return IntelFileSummary.model_validate(intel_file)


def find_existing_intel_file_for_raw_item(db: Session, raw_item_id: UUID) -> IntelFile | None:
    evidence = db.scalar(
        select(Evidence)
        .options(selectinload(Evidence.intel_file))
        .where(
            Evidence.raw_item_id == raw_item_id,
            Evidence.evidence_type == EvidenceType.FIRST_SEEN,
        )
    )
    if evidence is None:
        return None
    return evidence.intel_file


def create_intel_file(
    db: Session,
    payload: IntelFileCreateRequest,
    *,
    workspace_id: UUID | None = None,
) -> IntelFile:
    existing = find_existing_intel_file_for_raw_item(db, payload.raw_item_id)
    if existing is not None:
        if workspace_id is not None and existing.workspace_id != workspace_id:
            raise ValueError("Intel file not found.")
        return existing

    raw_item = db.scalar(
        select(RawItem)
        .options(selectinload(RawItem.signal_analysis))
        .where(RawItem.id == payload.raw_item_id)
    )
    if raw_item is None:
        raise ValueError("Raw item not found.")
    if workspace_id is not None and raw_item.workspace_id != workspace_id:
        raise ValueError("Raw item not found.")

    analysis = raw_item.signal_analysis
    if analysis is None:
        raise IntelFileError(
            "Raw item has no signal analysis. Analyze the signal before creating an intel file."
        )

    if payload.analysis_id is not None and payload.analysis_id != analysis.id:
        raise IntelFileError("Analysis ID does not match the raw item's analysis.")

    seen_at = _resolve_seen_at(raw_item)
    title = payload.title.strip() if payload.title and payload.title.strip() else raw_item.title
    thesis = (
        payload.thesis.strip()
        if payload.thesis and payload.thesis.strip()
        else (analysis.rationale or analysis.summary)
    )

    intel_file = IntelFile(
        workspace_id=raw_item.workspace_id,
        title=title,
        thesis=thesis,
        status=LifecycleStatus.NEW,
        first_seen_at=seen_at,
        last_seen_at=seen_at,
        primary_signal_type=analysis.signal_type,
        entities=analysis.entities,
        keywords=analysis.keywords,
        source_count=1,
        evidence_count=1,
        heat_score=1.0,
        credibility_score=analysis.credibility_hint,
        opportunity_score=_initial_opportunity_score(analysis),
        risk_score=analysis.risk_hint,
    )
    db.add(intel_file)
    db.flush()

    evidence = Evidence(
        intel_file_id=intel_file.id,
        raw_item_id=raw_item.id,
        evidence_type=EvidenceType.FIRST_SEEN,
        confidence=1.0,
        attached_by=AttachedBy.USER,
        rationale="Initial evidence from manual promotion.",
    )
    db.add(evidence)
    db.flush()

    event = IntelEvent(
        intel_file_id=intel_file.id,
        event_type=IntelEventType.CREATED,
        event_time=seen_at,
        title="Intel file created",
        description=f"Promoted from analyzed signal: {title}",
        source_evidence_id=evidence.id,
        metadata_={
            "raw_item_id": str(raw_item.id),
            "analysis_id": str(analysis.id),
        },
    )
    db.add(event)
    db.commit()
    db.refresh(intel_file)
    return intel_file


def list_intel_files(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status: LifecycleStatus | None = None,
    q: str | None = None,
    sort: str = "updated_at",
    order: str = "desc",
    workspace_id: UUID | None = None,
) -> IntelFileListData:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    sort_columns = {
        "updated_at": IntelFile.updated_at,
        "last_seen_at": IntelFile.last_seen_at,
        "first_seen_at": IntelFile.first_seen_at,
        "opportunity_score": IntelFile.opportunity_score,
        "heat_score": IntelFile.heat_score,
        "risk_score": IntelFile.risk_score,
        "evidence_count": IntelFile.evidence_count,
    }
    sort_column = sort_columns.get(sort, IntelFile.updated_at)
    sort_direction = asc if order == "asc" else desc

    query = select(IntelFile)
    count_query = select(func.count()).select_from(IntelFile)

    if status is not None:
        query = query.where(IntelFile.status == status)
        count_query = count_query.where(IntelFile.status == status)
    if q is not None and q.strip():
        pattern = f"%{q.strip()}%"
        search_filter = or_(
            IntelFile.title.ilike(pattern),
            IntelFile.thesis.ilike(pattern),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    if workspace_id is not None:
        query = query.where(IntelFile.workspace_id == workspace_id)
        count_query = count_query.where(IntelFile.workspace_id == workspace_id)

    total = db.scalar(count_query) or 0
    items = db.scalars(
        query.order_by(sort_direction(sort_column), IntelFile.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return IntelFileListData(
        items=[to_intel_file_summary(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_intel_file_detail(
    db: Session,
    intel_file_id: UUID,
    *,
    workspace_id: UUID | None = None,
) -> IntelFileDetailData:
    intel_file = db.scalar(
        select(IntelFile)
        .options(
            selectinload(IntelFile.evidence),
            selectinload(IntelFile.events),
        )
        .where(IntelFile.id == intel_file_id)
    )
    if intel_file is None:
        raise ValueError("Intel file not found.")
    if workspace_id is not None and intel_file.workspace_id != workspace_id:
        raise ValueError("Intel file not found.")

    novelty_score: float | None = None
    if intel_file.evidence:
        first_evidence = next(
            (item for item in intel_file.evidence if item.evidence_type == EvidenceType.FIRST_SEEN),
            intel_file.evidence[0],
        )
        analysis = db.scalar(
            select(SignalAnalysis).where(SignalAnalysis.raw_item_id == first_evidence.raw_item_id)
        )
        if analysis is not None:
            novelty_score = analysis.novelty_score

    timeline = sorted(intel_file.events, key=lambda event: event.event_time)

    return IntelFileDetailData(
        intel_file=to_intel_file_summary(intel_file),
        novelty_score=novelty_score,
        evidence=[EvidenceSummary.model_validate(item) for item in intel_file.evidence],
        timeline=[IntelEventSummary.model_validate(item) for item in timeline],
        snapshots=[],
        alerts=[],
    )


def raw_item_ids_with_intel_file(db: Session, raw_item_ids: list[UUID]) -> set[UUID]:
    if not raw_item_ids:
        return set()
    rows = db.scalars(
        select(Evidence.raw_item_id).where(
            Evidence.raw_item_id.in_(raw_item_ids),
            Evidence.evidence_type == EvidenceType.FIRST_SEEN,
        )
    ).all()
    return set(rows)
