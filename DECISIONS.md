# DECISIONS.md

Architecture Decision Records for Signal Tracker.

## ADR-20260522-01: Use IntelFile As The Primary Product Object

### Context

The product must track the lifecycle of signals over time. A generic article/news model would optimize for individual items rather than continuity.

### Decision

Use `IntelFile` as the primary product object. Raw articles, posts, screenshots, and links are stored as `RawItem` and attached as `Evidence`.

### Alternatives Considered

1. Article-first model.
2. Tag-based news archive.
3. Entity graph as the primary object.

### Consequences

- UI should center on intel files and timelines.
- Evidence can come from many source types.
- First-seen and lifecycle history are preserved.
- Matching and merge logic become important early.

### Follow-up Tasks

- Implement `IntelFile`, `Evidence`, and `IntelEvent` in P1.

## ADR-20260522-02: Start With Manual Intake Before Full Crawling

### Context

Automated crawling can explode scope and compliance risk before the core product loop is proven.

### Decision

The MVP starts with manual URL/text submission and optional limited source checks. Large-scale social crawling is deferred.

### Alternatives Considered

1. Start with X/Reddit/GitHub crawlers.
2. Build an RSS reader first.
3. Use only browser bookmarks.

### Consequences

- MVP can focus on extraction, file creation, evidence, lifecycle, scoring, and briefing.
- Source connectors can be added after the domain model proves useful.

### Follow-up Tasks

- Define manual submission flow in P1.
- Add tracking connectors in P2.

## ADR-20260522-03: Use Explainable Formula Scoring In V1

### Context

Users must trust opportunity, credibility, heat, and risk scores. A black-box model would be hard to debug and hard to explain.

### Decision

Use formula-based v1 scoring with stored rationale and score snapshots.

### Alternatives Considered

1. Let AI assign all scores directly.
2. Train or tune a model.
3. No scoring in MVP.

### Consequences

- Scores are inspectable.
- Initial formulas may be imperfect but easy to adjust.
- AI can still provide input features and rationale.

### Follow-up Tasks

- Implement scoring engine with snapshot storage.
- Add score explanation UI.

## ADR-20260522-04: Use Conservative Evidence Matching

### Context

Wrongly merging unrelated evidence into a file can corrupt the intelligence history.

### Decision

MVP matching should be conservative. When confidence is below a threshold, create a suggestion instead of auto-attaching.

### Alternatives Considered

1. Aggressive auto-merge using embeddings.
2. Fully manual attachment.
3. Keyword-only matching.

### Consequences

- Fewer false merges.
- More review steps may be needed.
- Matching confidence and rationale must be visible.

### Follow-up Tasks

- Implement matching suggestions after MVP file creation works.

## ADR-20260522-05: Lifecycle Transitions Must Be Logged

### Context

The product promise depends on explaining how a signal moved from new to dormant, resurrected, verified, or noise.

### Decision

Every lifecycle transition creates an `IntelEvent` and `LifecycleSnapshot` with reason and evidence references.

### Alternatives Considered

1. Store only current status.
2. Store status changes in raw logs.
3. Let frontend infer status history.

### Consequences

- Timeline and auditability are first-class.
- Storage is slightly larger.
- State changes can be tested.

### Follow-up Tasks

- Implement lifecycle engine and snapshot tests.

## ADR-20260523-06: Nullable RawItem Content For URL-Only Intake

### Context

Manual submission (TASK-P1-03) must accept URL-only input before page content is fetched or pasted.

### Decision

Allow `RawItem.content` to be nullable. Intake derives `content_hash` from URL and/or content; extraction may run after content backfill.

### Consequences

- URL-only items can enter the inbox immediately.
- Downstream extraction must tolerate missing content until fetch completes.
- `content_hash` dedupe must not assume content is present.

## ADR-20260523-07: Persist Full AI Extraction Fields On SignalAnalysis

### Context

The AI extraction contract (`signal_extract_v1`) returns tracking queries, risk hints, opportunity types, and rationale. These fields support P1-04 extraction and later tracking/briefing tasks.

### Decision

Persist `suggested_tracking_queries`, `risk_hint`, `opportunity_types`, and `rationale` on `SignalAnalysis` alongside existing score and entity fields.

### Consequences

- Extraction output maps directly to the domain model without stuffing everything into `raw_output`.
- Tracking query generation (P2) can read structured fields.
- Schema and migration must stay aligned with `docs/specs/ai-extraction-contract.md`.
