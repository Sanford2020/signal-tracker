# Proposal: P1-06 Evidence Timeline

## Intent

Attach additional `RawItem` records as evidence to an existing `IntelFile` and surface creation plus evidence-added events on the file timeline.

## Scope

In: attach evidence API, file counter updates, timeline events, detail UI form, tests.
Out: automated matching, lifecycle engine, scoring, alerts, graph UI.

## Success

Follow-up evidence attaches with metadata, duplicates are rejected, file counts and `last_seen_at` update, timeline shows ordered events.
