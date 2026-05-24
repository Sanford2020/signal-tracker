import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Evidence, IntelEvent, IntelFile, LifecycleSnapshot, RawItem, SignalAnalysis
from app.models.enums import EvidenceType, IntelEventType, SignalType
from app.modules.alerts.service import process_score_alerts
from app.schemas.scoring import ScoreUpdateData, ScoreUpdateRequest

TRUST_TIER_BASE = {0: 8.0, 1: 6.5, 2: 4.5, 3: 2.5}


def clamp_score(value: float) -> float:
    return round(max(0.0, min(10.0, value)), 1)


def _trust_base(trust_tier: int) -> float:
    return TRUST_TIER_BASE.get(trust_tier, TRUST_TIER_BASE[2])


@dataclass
class ScoringContext:
    intel_file: IntelFile
    evidence: list[Evidence]
    first_analysis: SignalAnalysis | None
    trust_tiers: list[int]
    corroboration_count: int
    contradiction_count: int
    correction_count: int


def _build_context(intel_file: IntelFile, first_analysis: SignalAnalysis | None) -> ScoringContext:
    evidence = list(intel_file.evidence)
    trust_tiers: list[int] = []
    for item in evidence:
        if item.raw_item and item.raw_item.source:
            trust_tiers.append(item.raw_item.source.trust_tier)

    return ScoringContext(
        intel_file=intel_file,
        evidence=evidence,
        first_analysis=first_analysis,
        trust_tiers=trust_tiers or [2],
        corroboration_count=sum(
            1 for item in evidence if item.evidence_type == EvidenceType.CORROBORATION
        ),
        contradiction_count=sum(
            1 for item in evidence if item.evidence_type == EvidenceType.CONTRADICTION
        ),
        correction_count=sum(
            1 for item in evidence if item.evidence_type == EvidenceType.CORRECTION
        ),
    )


def calculate_novelty(ctx: ScoringContext) -> tuple[float, dict[str, Any]]:
    analysis = ctx.first_analysis
    base = analysis.novelty_score if analysis and analysis.novelty_score is not None else 5.0
    entity_bonus = min(2.0, len(ctx.intel_file.entities) * 0.5)
    keyword_bonus = min(1.0, len(ctx.intel_file.keywords) * 0.25)
    avg_trust = sum(ctx.trust_tiers) / len(ctx.trust_tiers)
    source_earliness = (avg_trust / 3.0) * 3.0
    low_coverage = 2.0 if ctx.intel_file.evidence_count <= 2 else 0.5
    raw = 0.35 * base + entity_bonus + keyword_bonus + source_earliness + low_coverage
    inputs = {
        "analysis_novelty": base,
        "entity_bonus": entity_bonus,
        "keyword_bonus": keyword_bonus,
        "source_earliness": round(source_earliness, 2),
        "low_coverage_bonus": low_coverage,
    }
    return clamp_score(raw), inputs


def calculate_heat(ctx: ScoringContext) -> tuple[float, dict[str, Any]]:
    evidence_component = float(ctx.intel_file.evidence_count)
    source_component = 2.0 * float(ctx.intel_file.source_count)
    corroboration_component = 1.5 * float(ctx.corroboration_count)
    raw = evidence_component + source_component + corroboration_component
    inputs = {
        "evidence_count": ctx.intel_file.evidence_count,
        "source_count": ctx.intel_file.source_count,
        "corroboration_count": ctx.corroboration_count,
        "evidence_component": evidence_component,
        "source_component": source_component,
        "corroboration_component": corroboration_component,
    }
    return clamp_score(raw * 0.9), inputs


def calculate_credibility(ctx: ScoringContext) -> tuple[float, dict[str, Any]]:
    trust_values = [_trust_base(tier) for tier in ctx.trust_tiers]
    source_trust = sum(trust_values) / len(trust_values)
    corroboration_bonus = min(3.0, ctx.corroboration_count * 1.5)
    contradiction_penalty = ctx.contradiction_count * 2.0 + ctx.correction_count * 1.0
    analysis_hint = (
        ctx.first_analysis.credibility_hint
        if ctx.first_analysis and ctx.first_analysis.credibility_hint is not None
        else 0.0
    )
    hint_component = analysis_hint * 0.25
    raw = source_trust + corroboration_bonus + hint_component - contradiction_penalty
    inputs = {
        "average_source_trust": round(source_trust, 2),
        "corroboration_bonus": corroboration_bonus,
        "contradiction_penalty": contradiction_penalty,
        "analysis_credibility_hint_component": round(hint_component, 2),
        "trust_tiers": ctx.trust_tiers,
    }
    return clamp_score(raw), inputs


def calculate_risk(ctx: ScoringContext) -> tuple[float, dict[str, Any]]:
    analysis = ctx.first_analysis
    base = analysis.risk_hint if analysis and analysis.risk_hint is not None else 3.0
    contradiction_penalty = ctx.contradiction_count * 1.5 + ctx.correction_count * 1.0
    avg_trust = sum(ctx.trust_tiers) / len(ctx.trust_tiers)
    low_trust = (avg_trust / 3.0) * 3.0
    rumor_penalty = 2.0 if ctx.intel_file.primary_signal_type == SignalType.RUMOR else 0.0
    corroboration_reduction = min(2.0, ctx.corroboration_count * 0.5)
    raw = base + contradiction_penalty + low_trust + rumor_penalty - corroboration_reduction
    inputs = {
        "analysis_risk_hint": base,
        "contradiction_penalty": contradiction_penalty,
        "low_trust_component": round(low_trust, 2),
        "rumor_penalty": rumor_penalty,
        "corroboration_reduction": corroboration_reduction,
    }
    return clamp_score(raw), inputs


def calculate_opportunity(
    ctx: ScoringContext,
    *,
    novelty: float,
    heat: float,
    credibility: float,
    risk: float,
) -> tuple[float, dict[str, Any]]:
    analysis = ctx.first_analysis
    relevance = analysis.relevance_score if analysis and analysis.relevance_score is not None else 5.0
    interest = min(10.0, len(analysis.opportunity_types) * 2.0) if analysis else 0.0
    raw = (
        0.25 * novelty
        + 0.20 * heat
        + 0.25 * relevance
        + 0.20 * credibility
        + 0.10 * interest
        - 0.20 * risk
    )
    inputs = {
        "novelty": novelty,
        "heat": heat,
        "relevance": relevance,
        "credibility": credibility,
        "interest": interest,
        "risk": risk,
    }
    return clamp_score(raw), inputs


def calculate_scores(ctx: ScoringContext) -> tuple[dict[str, float], dict[str, Any], str]:
    novelty, novelty_inputs = calculate_novelty(ctx)
    heat, heat_inputs = calculate_heat(ctx)
    credibility, credibility_inputs = calculate_credibility(ctx)
    risk, risk_inputs = calculate_risk(ctx)
    opportunity, opportunity_inputs = calculate_opportunity(
        ctx,
        novelty=novelty,
        heat=heat,
        credibility=credibility,
        risk=risk,
    )

    scores = {
        "novelty_score": novelty,
        "heat_score": heat,
        "credibility_score": credibility,
        "opportunity_score": opportunity,
        "risk_score": risk,
    }
    inputs = {
        "novelty": novelty_inputs,
        "heat": heat_inputs,
        "credibility": credibility_inputs,
        "opportunity": opportunity_inputs,
        "risk": risk_inputs,
        "evidence_count": ctx.intel_file.evidence_count,
        "source_count": ctx.intel_file.source_count,
    }
    rationale = (
        "Scores updated from evidence count, source trust tiers, corroboration/contradiction "
        f"evidence, and first analysis hints (novelty={novelty}, heat={heat}, "
        f"credibility={credibility}, opportunity={opportunity}, risk={risk})."
    )
    return scores, inputs, rationale


def _score_changes(
    previous: dict[str, float | None],
    current: dict[str, float],
) -> dict[str, list[float | None]]:
    return {
        "novelty_score": [previous.get("novelty_score"), current["novelty_score"]],
        "heat_score": [previous.get("heat_score"), current["heat_score"]],
        "credibility_score": [previous.get("credibility_score"), current["credibility_score"]],
        "opportunity_score": [previous.get("opportunity_score"), current["opportunity_score"]],
        "risk_score": [previous.get("risk_score"), current["risk_score"]],
    }


def _load_first_analysis(db: Session, evidence: list[Evidence]) -> SignalAnalysis | None:
    if not evidence:
        return None
    first_evidence = next(
        (item for item in evidence if item.evidence_type == EvidenceType.FIRST_SEEN),
        evidence[0],
    )
    return db.scalar(
        select(SignalAnalysis).where(SignalAnalysis.raw_item_id == first_evidence.raw_item_id)
    )


def score_intel_file(
    db: Session,
    intel_file_id: UUID,
    payload: ScoreUpdateRequest,
) -> ScoreUpdateData:
    intel_file = db.scalar(
        select(IntelFile)
        .options(
            selectinload(IntelFile.evidence).selectinload(Evidence.raw_item).selectinload(RawItem.source)
        )
        .where(IntelFile.id == intel_file_id)
    )
    if intel_file is None:
        raise ValueError("Intel file not found.")

    previous_scores = {
        "novelty_score": None,
        "heat_score": intel_file.heat_score,
        "credibility_score": intel_file.credibility_score,
        "opportunity_score": intel_file.opportunity_score,
        "risk_score": intel_file.risk_score,
    }

    first_analysis = _load_first_analysis(db, list(intel_file.evidence))
    ctx = _build_context(intel_file, first_analysis)
    scores, inputs, rationale = calculate_scores(ctx)

    intel_file.heat_score = scores["heat_score"]
    intel_file.credibility_score = scores["credibility_score"]
    intel_file.opportunity_score = scores["opportunity_score"]
    intel_file.risk_score = scores["risk_score"]

    now = datetime.now(UTC)
    snapshot_reason = json.dumps(
        {
            "summary": rationale,
            "trigger": payload.reason,
            "novelty_score": scores["novelty_score"],
            "inputs": inputs,
        }
    )
    snapshot = LifecycleSnapshot(
        intel_file_id=intel_file.id,
        snapshot_time=now,
        status=intel_file.status,
        heat_score=scores["heat_score"],
        credibility_score=scores["credibility_score"],
        opportunity_score=scores["opportunity_score"],
        risk_score=scores["risk_score"],
        reason=snapshot_reason,
    )
    db.add(snapshot)

    score_changes = _score_changes(previous_scores, scores)
    changed = any(
        previous_scores[key] != scores[key]
        for key in ("heat_score", "credibility_score", "opportunity_score", "risk_score")
    )

    if changed:
        event = IntelEvent(
            intel_file_id=intel_file.id,
            event_type=IntelEventType.SCORE_CHANGED,
            event_time=now,
            title="Scores updated",
            description=rationale,
            metadata_={
                "score_changes": score_changes,
                "novelty_score": scores["novelty_score"],
                "inputs": inputs,
                "trigger": payload.reason,
            },
        )
        db.add(event)

    process_score_alerts(db, intel_file, score_changes)

    db.commit()
    db.refresh(intel_file)

    return ScoreUpdateData(
        novelty_score=scores["novelty_score"],
        heat_score=scores["heat_score"],
        credibility_score=scores["credibility_score"],
        opportunity_score=scores["opportunity_score"],
        risk_score=scores["risk_score"],
        score_changes=score_changes,
        rationale=rationale,
        inputs=inputs,
        snapshot_time=now,
    )
