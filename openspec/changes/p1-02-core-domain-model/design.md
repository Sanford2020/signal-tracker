# Design: P1-02 Core Domain Model

## Technical Approach

Use relational tables for the MVP domain model. Keep JSON fields for flexible AI outputs and entity arrays, but keep primary relationships explicit.

## Entities

### Source

Stores source metadata, source type, trust tier, and fetch policy.

### RawItem

Immutable raw captured item with source, content, URL, timestamps, hash, and raw payload.

### SignalAnalysis

Structured analysis for one raw item.

### IntelFile

Primary product object. Stores title, thesis, status, timestamps, entities, keywords, counts, and latest scores.

### Evidence

Join record linking raw items to intel files with evidence role and rationale.

### IntelEvent

Timeline event for file creation, evidence attachment, status changes, score changes, and notes.

### LifecycleSnapshot

Point-in-time lifecycle state and score snapshot.

### AlertEvent

Notification-worthy event linked to an intel file.

## Constraints

- `RawItem.content_hash` should support dedupe.
- `SignalAnalysis.raw_item_id` should be unique for MVP unless multiple prompt versions are explicitly supported later.
- Evidence should prevent duplicate `(intel_file_id, raw_item_id)` rows.
- `IntelFile.status` should be constrained to lifecycle states.
- Score values should support 0-10 values.

## Design Decisions

### Decision: Separate RawItem And Evidence

A raw item is a captured fact. Evidence is the role that fact plays in a file.

### Decision: Store Current Scores On IntelFile

This supports fast list views. Full score history lives in snapshots.

### Decision: Use JSON For Entities And Keywords In MVP

This avoids overbuilding an entity graph before the core lifecycle loop is proven.

## Test Strategy

- Test model creation.
- Test relationship navigation.
- Test duplicate raw item hash handling.
- Test duplicate evidence prevention.
- Test status enum validation if supported by chosen stack.
