# Design: P2-01 Tracking Query Generation

## Flow

```text
POST /api/v1/intel-files/{id}/tracking-queries
  -> load IntelFile + first SignalAnalysis
  -> build candidate queries
  -> normalize and dedupe
  -> persist TrackingQuery rows
```

## Sources

- `SignalAnalysis.suggested_tracking_queries`
- entities
- keywords
- IntelFile title/thesis
- primary signal type

## Rules

- Keep queries short enough for search systems.
- Deduplicate by normalized lowercase query per IntelFile.
- Regeneration returns existing rows and only inserts missing queries.
- No external network calls.
