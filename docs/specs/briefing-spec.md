# Briefing Spec

## Purpose

The daily briefing is the operator's working summary. It should surface changes that matter, not every raw item.

## Time Window

Default:

- Last 24 hours.

Configurable:

- 24h
- 48h
- 72h
- 7d

## Sections

### New Intel Files

Include files created in the window.

Sort:

1. opportunity_score descending
2. novelty_score descending
3. created_at descending

### Updated Intel Files

Include files with new evidence or score changes in the window.

Exclude files already in resurrected section unless they also meet high-opportunity threshold.

### Resurrected Signals

Include files with lifecycle transition to `resurrected` in the window.

This is a premium section. Keep it near the top.

### High Opportunity

Include files where:

- opportunity_score >= configured threshold, default 7
- or opportunity score increased by >= 2 in window

### Risk Or Noise Candidates

Include files where:

- risk_score >= 7
- or status changed to `noise`
- or status changed to `debunked`

## Briefing Item Fields

```json
{
  "intel_file_id": 1,
  "title": "Example AI hiring for hardware roles",
  "status": "resurrected",
  "reason": "New primary-source job post after 19 days of inactivity.",
  "scores": {
    "heat": 6.8,
    "credibility": 6.5,
    "opportunity": 7.4,
    "risk": 2.1
  },
  "key_evidence": [
    {
      "raw_item_id": 12,
      "title": "Hardware supply chain lead role",
      "url": "https://example.com/jobs/123"
    }
  ]
}
```

## Overview Text

The briefing may generate a concise overview:

```text
Today: 4 new intel files, 3 meaningful updates, 1 resurrected signal, 2 high-opportunity files, and 1 risk/noise candidate.
```

## Exclusions

Do not include:

- duplicate evidence without new meaning
- low-score raw items that did not become files
- alerts already dismissed before briefing generation

## MVP Acceptance

- Briefing can be generated from stored DB state.
- Empty briefing is still useful and explains what is missing.
- Resurrected files appear reliably.
