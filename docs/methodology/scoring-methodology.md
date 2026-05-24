# Scoring Methodology

## Purpose

Signal Tracker uses explainable scores to help users compare signals without turning the system into a black box.

All v1 scores are 0 to 10.

## Score Types

| Score | Question |
| --- | --- |
| Novelty | Is this early, unusual, or undercovered? |
| Heat | Is attention increasing? |
| Credibility | Is the evidence trustworthy? |
| Opportunity | Could this become useful commercially, strategically, technically, or creatively? |
| Risk | Could this be false, misleading, dangerous, or a scam? |

## Novelty Score

Novelty estimates whether the signal appears early.

Suggested inputs:

- Source type: weak-signal sources score higher than mainstream repeats.
- First-seen freshness.
- Number of prior matching intel files.
- Whether the item contains a new entity/claim combination.

V1 formula:

```text
novelty =
  3.0 * source_earliness
+ 3.0 * claim_newness
+ 2.0 * entity_combination_newness
+ 2.0 * low_prior_coverage
```

## Heat Score

Heat estimates current momentum.

V1 formula:

```text
heat =
  evidence_count_recent
+ 2.0 * distinct_source_count_recent
+ 3.0 * high_relevance_evidence_recent
+ trend_bonus
- duplicate_penalty
```

Normalize to 0-10 after calculation.

## Credibility Score

Credibility estimates whether the claim is supported.

Suggested source tiers:

| Tier | Meaning | Base contribution |
| --- | --- | --- |
| 0 | Primary or highly reliable source | High |
| 1 | Reliable secondary source | Medium-high |
| 2 | Social or unverified but useful source | Medium-low |
| 3 | Unknown or low-trust source | Low |

V1 formula:

```text
credibility =
  source_trust_score
+ corroboration_bonus
+ primary_evidence_bonus
- contradiction_penalty
- rumor_penalty
```

## Opportunity Score

Opportunity estimates whether the signal might become valuable.

Opportunity types:

- product opportunity
- startup opportunity
- investment clue
- content opportunity
- technical opportunity
- policy/compliance opportunity
- career opportunity

V1 formula:

```text
opportunity =
  0.25 * novelty
+ 0.20 * heat
+ 0.25 * relevance
+ 0.20 * credibility
+ 0.10 * user_interest_match
- 0.20 * risk
```

Clamp final value to 0-10.

## Risk Score

Risk estimates whether the signal is likely harmful, false, or low quality.

V1 formula:

```text
risk =
  rumor_penalty
+ low_source_trust
+ contradiction_count
+ scam_pattern_score
+ hype_without_evidence
- primary_evidence_bonus
```

## Relevance Score

Relevance measures alignment with the user's watch themes.

Examples:

- AI hardware
- agent tooling
- open-source AI
- policy changes
- platform rules
- enterprise software
- cybersecurity

V1 can be AI-assigned but must store rationale.

## Status Thresholds

Suggested defaults:

| Condition | Result |
| --- | --- |
| heat >= 7 and source_count >= 3 | spreading |
| credibility >= 7 and primary evidence exists | validating |
| credibility >= 8.5 and contradictions low | verified |
| risk >= 8 and credibility <= 3 | noise or debunk candidate |
| dormant file gets heat >= 4 or primary evidence | resurrected |
| opportunity >= 7 | opportunity alert |

## Score Snapshot

Every score update should be stored as a snapshot:

```json
{
  "intel_file_id": 42,
  "snapshot_time": "2026-05-22T14:00:00Z",
  "novelty_score": 8.2,
  "heat_score": 5.7,
  "credibility_score": 6.1,
  "opportunity_score": 7.3,
  "risk_score": 3.2,
  "reason": "New GitHub release and two independent discussions increased heat and technical opportunity."
}
```

## Explainability Requirement

Every score shown in UI should expose:

- Inputs used.
- Last changed time.
- Reason for change.
- Evidence that caused the change.

## MVP Rule

Prefer a simple formula users can inspect over a sophisticated model users cannot trust.
