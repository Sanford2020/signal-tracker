# Proposal: P1-07 Lifecycle Evaluation V1

## Intent

Add a deterministic lifecycle evaluation engine that proposes status transitions for `IntelFile` records, persists snapshots, and logs status-change events.

## Scope

In: lifecycle service, evaluate API, configurable dormancy, unit tests.
Out: scoring recalculation, alerts, briefing, AI decisions, lifecycle UI.

## Success

`POST /api/v1/intel-files/{id}/evaluate` returns transition rationale, evidence IDs, score changes, and persists snapshots/events.
