# Proposal: P2-01 Tracking Query Generation

## Intent

Create deterministic follow-up tracking queries for IntelFiles.

## Scope

In: tracking query persistence, generation service, API, tests.
Out: external fetching, scheduled workers, matching suggestions.

## Success

An IntelFile can produce a stable, deduplicated list of enabled tracking queries that P2 workers can later consume.
