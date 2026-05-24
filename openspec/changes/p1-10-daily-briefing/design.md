# Design: P1-10 Daily Briefing V1

## Flow

```text
GET /api/v1/briefings/daily?hours=24&min_opportunity=7
  -> collect IntelFile rows and recent IntelEvent rows
  -> group into briefing sections
  -> include key evidence and score summary
```

## Sections

- new_files: IntelFiles created in the window.
- updated_files: files with evidence_added or score_changed events in the window.
- resurrected: files with status_changed events to resurrected in the window.
- high_opportunity: files with opportunity_score >= threshold or score_changed crossing the threshold.
- risk_or_noise: files with risk_score >= 7 or status noise/debunked or matching status_changed events.

## Boundaries

- No external delivery.
- No AI narrative generation.
- No lifecycle or scoring mutations.
