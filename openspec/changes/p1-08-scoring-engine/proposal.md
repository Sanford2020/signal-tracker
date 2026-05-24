# Proposal: P1-08 Scoring Engine V1

## Intent

Add deterministic, explainable scoring for `IntelFile` records with persisted snapshots and inspectable inputs.

## Scope

In: scoring service, POST /score API, snapshot persistence, unit tests.
Out: AI scoring, lifecycle transitions, alerts, briefing.

## Success

All v1 scores are calculated, clamped 0-10, rationale stored, and tests cover normal/high-risk/high-opportunity/low-credibility cases.
