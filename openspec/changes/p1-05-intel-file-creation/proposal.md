# Proposal: P1-05 Intel File Creation

## Intent

Let users promote an analyzed `RawItem` / `SignalAnalysis` into a durable `IntelFile` with initial evidence and timeline event.

## Scope

In: promote API, list/detail skeleton APIs, inbox action, intel files UI, tests.
Out: matching/merge, lifecycle engine, scoring recalculation, alerts, briefing, crawlers, auth.

## Success

User can create an intel file from analyzed inbox item; duplicate promotion is idempotent; first evidence and creation event are stored; file appears in list and detail.
