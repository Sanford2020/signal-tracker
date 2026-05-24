# Proposal: P1-04 AI Extraction

## Intent

Turn submitted `RawItem` records into structured `SignalAnalysis` using a deterministic mock extractor by default.

## Scope

In: extraction service, prompt contract, mock fallback, analyze API, tests.
Out: IntelFile, lifecycle, scoring engines, alerts, briefing, crawlers.

## Success

`POST /api/v1/raw-items/{id}/analyze` stores analysis with all contract fields; tests pass without API key.
