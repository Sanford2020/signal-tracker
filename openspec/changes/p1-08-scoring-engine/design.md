# Design: P1-08 Scoring Engine V1

## Formulas (v1 simplified)

| Score | Inputs |
| --- | --- |
| Novelty | analysis novelty, entities/keywords, source earliness (inverse trust tier), low coverage |
| Heat | evidence_count, source_count, corroboration count |
| Credibility | source trust tiers, corroboration bonus, contradiction/correction penalties, analysis hint |
| Opportunity | 0.25×novelty + 0.20×heat + 0.25×relevance + 0.20×credibility + 0.10×interest − 0.20×risk |
| Risk | analysis risk hint, contradictions, low trust, rumor signal type |

Novelty is returned in API output and stored in snapshot reason JSON (no IntelFile column yet).

## Persistence

- Update `IntelFile` heat/credibility/opportunity/risk scores.
- Create `LifecycleSnapshot` with scores and JSON reason (summary + inputs + novelty).
- Create `IntelEvent` with `score_changed` when any stored score changes.

## Boundaries

Scoring does not call lifecycle evaluation or mutate `IntelFile.status`.
