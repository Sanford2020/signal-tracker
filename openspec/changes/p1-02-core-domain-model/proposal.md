# Proposal: P1-02 Core Domain Model

## Intent

Implement the core persistent domain model for Signal Tracker.

## Problem

The product depends on durable intelligence files and evidence history. Without the domain model, later tasks cannot implement intake, extraction, lifecycle, scoring, alerts, or briefing safely.

## Scope

In scope:

- Source model.
- RawItem model.
- SignalAnalysis model.
- IntelFile model.
- Evidence model.
- IntelEvent model.
- LifecycleSnapshot model.
- AlertEvent model.
- Migrations.
- Basic schema/read models.
- Relationship tests.

Out of scope:

- Full API routes beyond what is needed for tests.
- UI.
- AI extraction logic.
- Lifecycle engine logic.
- Scoring formulas.
- External notifications.

## Approach

Follow `docs/architecture/data-model.md`. Keep `IntelFile` as the primary product object, and keep `RawItem` immutable.

Implement enough model behavior to create a complete sample chain in tests:

```text
Source
  -> RawItem
  -> SignalAnalysis
  -> IntelFile
  -> Evidence
  -> IntelEvent
  -> LifecycleSnapshot
  -> AlertEvent
```

## Success

Tests can create and query the full MVP domain chain, and migrations can create the required tables.
