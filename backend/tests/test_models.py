from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    AlertChannel,
    AlertEvent,
    AlertSeverity,
    AlertStatus,
    AlertType,
    AttachedBy,
    Evidence,
    EvidenceType,
    IntelEvent,
    IntelEventType,
    IntelFile,
    LifecycleSnapshot,
    LifecycleStatus,
    RawItem,
    SignalAnalysis,
    SignalType,
    Source,
    SourceType,
)


def _ts() -> datetime:
    return datetime(2026, 5, 23, 12, 0, 0)


def test_create_source_and_raw_item(db_session: Session) -> None:
    source = Source(name="Manual Intake", source_type=SourceType.MANUAL, trust_tier=0)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="New AI framework rumor",
        content="A new framework may launch next week.",
        content_hash="abc123hash",
        captured_at=_ts(),
    )
    db_session.add(raw_item)
    db_session.commit()

    stored = db_session.get(RawItem, raw_item.id)
    assert stored is not None
    assert stored.source.name == "Manual Intake"


def test_url_only_raw_item_allows_null_content(db_session: Session) -> None:
    source = Source(name="Manual Intake", source_type=SourceType.MANUAL, trust_tier=0)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="Pending fetch",
        url="https://example.com/signal-post",
        content=None,
        content_hash="url-only-hash",
        captured_at=_ts(),
    )
    db_session.add(raw_item)
    db_session.commit()

    stored = db_session.get(RawItem, raw_item.id)
    assert stored is not None
    assert stored.content is None
    assert stored.url == "https://example.com/signal-post"


def test_signal_analysis_persists_extraction_fields(db_session: Session) -> None:
    source = Source(name="Manual", source_type=SourceType.MANUAL)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="Example AI hiring hardware supply chain lead",
        content="Hiring post for hardware supply chain lead.",
        content_hash="extraction-fields-hash",
        captured_at=_ts(),
    )
    db_session.add(raw_item)
    db_session.flush()

    analysis = SignalAnalysis(
        raw_item_id=raw_item.id,
        summary="Example AI appears to be hiring for hardware supply chain roles.",
        signal_type=SignalType.HIRING,
        entities=[{"name": "Example AI", "type": "org"}],
        keywords=["Example AI", "hardware"],
        claims=[{"text": "Hiring for hardware supply chain", "claim_type": "inference"}],
        suggested_tracking_queries=["Example AI hardware hiring"],
        opportunity_types=["product", "technical"],
        novelty_score=7.0,
        relevance_score=8.0,
        credibility_hint=5.5,
        risk_hint=2.0,
        rationale="Early hiring signal tied to a possible product direction.",
        prompt_version="signal_extract_v1",
    )
    db_session.add(analysis)
    db_session.commit()

    stored = db_session.get(SignalAnalysis, analysis.id)
    assert stored is not None
    assert stored.suggested_tracking_queries == ["Example AI hardware hiring"]
    assert stored.opportunity_types == ["product", "technical"]
    assert stored.risk_hint == 2.0
    assert "product direction" in (stored.rationale or "")


def test_duplicate_content_hash_rejected(db_session: Session) -> None:
    source = Source(name="Manual", source_type=SourceType.MANUAL)
    db_session.add(source)
    db_session.flush()

    db_session.add(
        RawItem(
            source_id=source.id,
            title="First",
            content="alpha",
            content_hash="dup-hash",
            captured_at=_ts(),
        )
    )
    db_session.commit()

    db_session.add(
        RawItem(
            source_id=source.id,
            title="Second",
            content="beta",
            content_hash="dup-hash",
            captured_at=_ts(),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_signal_analysis_links_to_raw_item(db_session: Session) -> None:
    source = Source(name="GitHub", source_type=SourceType.GITHUB)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="Repo activity spike",
        content="Commits increased 300%.",
        content_hash="analysis-hash-1",
        captured_at=_ts(),
    )
    db_session.add(raw_item)
    db_session.flush()

    analysis = SignalAnalysis(
        raw_item_id=raw_item.id,
        summary="Open-source project activity increased sharply.",
        signal_type=SignalType.GITHUB,
        entities=[{"name": "ExampleOrg", "type": "organization"}],
        keywords=["github", "activity"],
        claims=["Activity spike detected"],
        novelty_score=7.5,
    )
    db_session.add(analysis)
    db_session.commit()

    assert raw_item.signal_analysis.summary.startswith("Open-source")


def test_intel_file_timestamps_and_evidence(db_session: Session) -> None:
    ts = _ts()
    source = Source(name="News", source_type=SourceType.NEWS)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="Funding rumor",
        content="Company X may raise Series B.",
        content_hash="intel-hash-1",
        captured_at=ts,
    )
    db_session.add(raw_item)
    db_session.flush()

    intel_file = IntelFile(
        title="Company X funding signal",
        thesis="Possible Series B in progress",
        status=LifecycleStatus.NEW,
        first_seen_at=ts,
        last_seen_at=ts,
        primary_signal_type=SignalType.FUNDING,
        entities=[{"name": "Company X", "type": "organization"}],
        keywords=["funding", "series-b"],
        source_count=1,
        evidence_count=1,
        heat_score=4.0,
    )
    db_session.add(intel_file)
    db_session.flush()

    evidence = Evidence(
        intel_file_id=intel_file.id,
        raw_item_id=raw_item.id,
        evidence_type=EvidenceType.FIRST_SEEN,
        confidence=0.92,
        attached_by=AttachedBy.SYSTEM,
        rationale="Initial capture",
    )
    db_session.add(evidence)
    db_session.commit()

    assert intel_file.first_seen_at == ts
    assert intel_file.last_seen_at == ts
    assert len(intel_file.evidence) == 1
    assert intel_file.evidence[0].raw_item.title == "Funding rumor"


def test_duplicate_evidence_rejected(db_session: Session) -> None:
    ts = _ts()
    source = Source(name="Manual", source_type=SourceType.MANUAL)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="Duplicate evidence test",
        content="content",
        content_hash="evidence-dup-hash",
        captured_at=ts,
    )
    intel_file = IntelFile(
        title="File",
        status=LifecycleStatus.NEW,
        first_seen_at=ts,
        last_seen_at=ts,
    )
    db_session.add_all([raw_item, intel_file])
    db_session.flush()

    db_session.add(
        Evidence(
            intel_file_id=intel_file.id,
            raw_item_id=raw_item.id,
            evidence_type=EvidenceType.FIRST_SEEN,
        )
    )
    db_session.commit()

    db_session.add(
        Evidence(
            intel_file_id=intel_file.id,
            raw_item_id=raw_item.id,
            evidence_type=EvidenceType.FOLLOW_UP,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_full_sample_chain(db_session: Session) -> None:
    ts = datetime(2026, 5, 23, 8, 30, 0)

    source = Source(name="X", source_type=SourceType.X, trust_tier=1)
    db_session.add(source)
    db_session.flush()

    raw_item = RawItem(
        source_id=source.id,
        title="Founder post about new model",
        url="https://example.com/post/1",
        content="We are launching a new model soon.",
        content_hash="full-chain-hash",
        captured_at=ts,
    )
    db_session.add(raw_item)
    db_session.flush()

    analysis = SignalAnalysis(
        raw_item_id=raw_item.id,
        summary="Founder hints at upcoming model launch.",
        signal_type=SignalType.PRODUCT,
        entities=[{"name": "Example AI", "type": "organization"}],
        keywords=["model", "launch"],
        claims=[{"text": "New model launch is imminent", "claim_type": "inference"}],
        suggested_tracking_queries=["Example AI model launch"],
        opportunity_types=["product", "startup"],
        relevance_score=8.0,
        credibility_hint=6.5,
        risk_hint=2.5,
        rationale="Founder post suggests imminent model launch.",
    )
    db_session.add(analysis)
    db_session.flush()

    intel_file = IntelFile(
        title="Example AI model launch signal",
        thesis="Product launch may be near",
        status=LifecycleStatus.WATCHING,
        first_seen_at=ts,
        last_seen_at=ts,
        primary_signal_type=SignalType.PRODUCT,
        entities=analysis.entities,
        keywords=analysis.keywords,
        source_count=1,
        evidence_count=1,
        heat_score=5.5,
        credibility_score=6.5,
        opportunity_score=7.0,
        risk_score=2.0,
    )
    db_session.add(intel_file)
    db_session.flush()

    evidence = Evidence(
        intel_file_id=intel_file.id,
        raw_item_id=raw_item.id,
        evidence_type=EvidenceType.FIRST_SEEN,
        confidence=0.88,
        attached_by=AttachedBy.SYSTEM,
        rationale="Initial signal from founder post",
    )
    db_session.add(evidence)
    db_session.flush()

    event = IntelEvent(
        intel_file_id=intel_file.id,
        event_type=IntelEventType.CREATED,
        event_time=ts,
        title="Intel file created",
        description="Initial file created from founder post",
        source_evidence_id=evidence.id,
        metadata_={"source_type": "x"},
    )
    snapshot = LifecycleSnapshot(
        intel_file_id=intel_file.id,
        snapshot_time=ts,
        status=LifecycleStatus.WATCHING,
        heat_score=5.5,
        credibility_score=6.5,
        opportunity_score=7.0,
        risk_score=2.0,
        reason="Initial evaluation",
    )
    alert = AlertEvent(
        intel_file_id=intel_file.id,
        alert_type=AlertType.OPPORTUNITY_UP,
        severity=AlertSeverity.WATCH,
        message="New product signal worth watching",
        status=AlertStatus.PENDING,
        channel=AlertChannel.IN_APP,
    )
    db_session.add_all([event, snapshot, alert])
    db_session.commit()

    loaded = db_session.get(IntelFile, intel_file.id)
    assert loaded is not None
    assert loaded.source_count == 1
    assert len(loaded.evidence) == 1
    assert len(loaded.events) == 1
    assert len(loaded.lifecycle_snapshots) == 1
    assert len(loaded.alerts) == 1
    assert loaded.evidence[0].raw_item.signal_analysis.signal_type == SignalType.PRODUCT
