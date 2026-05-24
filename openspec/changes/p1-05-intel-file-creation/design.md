# Design: P1-05 Intel File Creation

## Flow

```text
RawItem + SignalAnalysis
  -> POST /api/v1/intel-files
  -> IntelFile (status=new)
  -> Evidence (first_seen)
  -> IntelEvent (created)
```

## Duplicate policy

If `Evidence` with `first_seen` already exists for the `raw_item_id`, return the linked `IntelFile` idempotently.

## Initial field mapping

| IntelFile field | Source |
| --- | --- |
| title | request override or raw item title |
| thesis | request override or analysis rationale/summary |
| status | `new` |
| first_seen_at / last_seen_at | raw item published_at or captured_at |
| primary_signal_type | analysis.signal_type |
| entities / keywords | analysis |
| source_count / evidence_count | 1 |
| heat_score | 1.0 |
| credibility_score | analysis.credibility_hint |
| opportunity_score | average of relevance and novelty when present |
| risk_score | analysis.risk_hint |

## Boundaries

- Extraction never creates intel files.
- Promotion requires existing `SignalAnalysis`.
- No lifecycle transitions beyond initial `new` status.
