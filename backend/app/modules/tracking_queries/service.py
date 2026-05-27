import re
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models import Evidence, IntelFile, SignalAnalysis, TrackingQuery
from app.models.enums import EvidenceType, SignalType
from app.schemas.tracking_queries import TrackingQueryGenerateData, TrackingQueryGenerateRequest, TrackingQueryRead

MAX_QUERY_LENGTH = 160
PACKAGE_SIGNAL_TERMS = {
    "client",
    "library",
    "package",
    "packages",
    "pip",
    "pypi",
    "python",
    "sdk",
    "sdks",
}


@dataclass(frozen=True)
class CandidateQuery:
    query: str
    source_hint: str
    rationale: str


def normalize_query(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _clean_query(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())[:MAX_QUERY_LENGTH]


def _entity_names(intel_file: IntelFile) -> list[str]:
    names: list[str] = []
    for entity in intel_file.entities or []:
        if isinstance(entity, dict) and entity.get("name"):
            names.append(str(entity["name"]))
        elif isinstance(entity, str):
            names.append(entity)
    return names


def _load_first_analysis(db: Session, intel_file: IntelFile) -> SignalAnalysis | None:
    first_evidence = next(
        (item for item in intel_file.evidence if item.evidence_type == EvidenceType.FIRST_SEEN),
        intel_file.evidence[0] if intel_file.evidence else None,
    )
    if first_evidence is None:
        return None
    return db.scalar(
        select(SignalAnalysis).where(SignalAnalysis.raw_item_id == first_evidence.raw_item_id)
    )


def _source_hint(signal_type: SignalType | None) -> str:
    if signal_type == SignalType.GITHUB:
        return "github"
    if signal_type == SignalType.HIRING:
        return "careers"
    if signal_type == SignalType.RESEARCH:
        return "research"
    if signal_type == SignalType.FUNDING:
        return "funding"
    if signal_type == SignalType.MARKET:
        return "market"
    if signal_type == SignalType.POLICY:
        return "policy"
    return "search"


def _has_package_signal(intel_file: IntelFile, analysis: SignalAnalysis | None) -> bool:
    values = [
        intel_file.title,
        intel_file.thesis or "",
        *(str(item) for item in (intel_file.keywords or [])),
    ]
    if analysis is not None:
        values.extend(str(item) for item in (analysis.suggested_tracking_queries or []))
        values.extend(str(item) for item in (analysis.keywords or []))

    haystack = normalize_query(" ".join(values))
    return any(term in haystack.split() for term in PACKAGE_SIGNAL_TERMS)


def build_candidate_queries(intel_file: IntelFile, analysis: SignalAnalysis | None) -> list[CandidateQuery]:
    candidates: list[CandidateQuery] = []
    hint = _source_hint(intel_file.primary_signal_type)

    if analysis is not None:
        for query in analysis.suggested_tracking_queries or []:
            candidates.append(
                CandidateQuery(
                    query=str(query),
                    source_hint=hint,
                    rationale="Suggested by signal extraction.",
                )
            )

    entity_names = _entity_names(intel_file)
    keywords = [str(item) for item in (intel_file.keywords or []) if str(item).strip()]

    if _has_package_signal(intel_file, analysis):
        candidates.append(
            CandidateQuery(
                query=intel_file.title,
                source_hint="pypi",
                rationale="Python package or SDK release tracking.",
            )
        )

    for entity in entity_names[:4]:
        candidates.append(
            CandidateQuery(
                query=f"{entity} {intel_file.title}",
                source_hint=hint,
                rationale="Entity plus file title.",
            )
        )
        if intel_file.primary_signal_type is not None:
            candidates.append(
                CandidateQuery(
                    query=f"{entity} {intel_file.primary_signal_type.value}",
                    source_hint=hint,
                    rationale="Entity plus signal type.",
                )
            )

    for keyword in keywords[:6]:
        candidates.append(
            CandidateQuery(
                query=f"{keyword} {intel_file.primary_signal_type.value if intel_file.primary_signal_type else ''}",
                source_hint=hint,
                rationale="Keyword follow-up query.",
            )
        )

    if intel_file.thesis:
        candidates.append(
            CandidateQuery(
                query=f"{intel_file.title} {intel_file.thesis}",
                source_hint="search",
                rationale="Title plus thesis.",
            )
        )

    candidates.append(
        CandidateQuery(
            query=intel_file.title,
            source_hint=hint,
            rationale="File title fallback.",
        )
    )

    return candidates


def generate_tracking_queries(
    db: Session,
    intel_file_id: UUID,
    payload: TrackingQueryGenerateRequest,
    *,
    workspace_id: UUID | None = None,
) -> TrackingQueryGenerateData:
    intel_file = db.scalar(
        select(IntelFile)
        .options(selectinload(IntelFile.evidence), selectinload(IntelFile.tracking_queries))
        .where(IntelFile.id == intel_file_id)
    )
    if intel_file is None or (workspace_id is not None and intel_file.workspace_id != workspace_id):
        raise ValueError("Intel file not found.")

    if payload.regenerate:
        db.execute(delete(TrackingQuery).where(TrackingQuery.intel_file_id == intel_file.id))
        db.flush()

    analysis = _load_first_analysis(db, intel_file)
    existing = {
        item.normalized_query: item
        for item in db.scalars(
            select(TrackingQuery).where(TrackingQuery.intel_file_id == intel_file.id)
        ).all()
    }

    created_count = 0
    ordered: list[TrackingQuery] = list(existing.values())
    for candidate in build_candidate_queries(intel_file, analysis):
        query = _clean_query(candidate.query)
        normalized = normalize_query(query)
        if not normalized or normalized in existing:
            continue
        tracking_query = TrackingQuery(
            intel_file_id=intel_file.id,
            query=query,
            normalized_query=normalized,
            source_hint=candidate.source_hint,
            rationale=candidate.rationale,
            enabled=True,
            meta={
                "primary_signal_type": intel_file.primary_signal_type.value if intel_file.primary_signal_type else None,
            },
        )
        db.add(tracking_query)
        db.flush()
        existing[normalized] = tracking_query
        ordered.append(tracking_query)
        created_count += 1
        if len(ordered) >= max(1, min(payload.limit, 25)):
            break

    db.commit()
    rows = db.scalars(
        select(TrackingQuery)
        .where(TrackingQuery.intel_file_id == intel_file.id)
        .order_by(TrackingQuery.created_at.asc())
    ).all()

    return TrackingQueryGenerateData(
        items=[TrackingQueryRead.model_validate(item) for item in rows],
        created_count=created_count,
    )
