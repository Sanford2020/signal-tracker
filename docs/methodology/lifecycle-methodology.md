# Signal Lifecycle Methodology

## Purpose

This methodology defines how Signal Tracker treats information as a lifecycle object rather than a one-time news item.

The core unit is an `IntelFile`: a durable case file that gathers evidence over time.

## Lifecycle States

| State | Meaning |
| --- | --- |
| `new` | A signal has been seen for the first time and has limited evidence |
| `watching` | The signal is worth tracking, but not enough has changed yet |
| `spreading` | Multiple sources or communities are discussing it within a short window |
| `validating` | New evidence is increasing credibility or pointing toward confirmation |
| `cooling` | Activity is declining after initial attention |
| `dormant` | No meaningful evidence has appeared for a configured period |
| `resurrected` | A dormant signal receives meaningful new evidence |
| `verified` | The main claim is confirmed by strong evidence |
| `debunked` | The main claim is disproven or contradicted by strong evidence |
| `noise` | The signal is low-value, spammy, repetitive, or unsupported |
| `archived` | No longer actively tracked, but kept for history |

## Event Types

| Event type | Meaning |
| --- | --- |
| `first_seen` | Earliest known evidence for this signal |
| `new_evidence` | Additional evidence attached |
| `corroboration` | Evidence supports the main claim |
| `contradiction` | Evidence weakens or disputes the main claim |
| `mainstream_pickup` | Larger sources begin covering the signal |
| `source_expansion` | More distinct sources discuss the signal |
| `entity_expansion` | New people, companies, products, or regions are connected |
| `inactivity` | No meaningful update for a threshold period |
| `revival` | Meaningful evidence after dormancy |
| `verification` | Claim confirmed |
| `debunk` | Claim disproven |

## State Transition Rules

### New

Create `new` when:

- A raw item does not match an existing intel file.
- It contains a non-trivial claim, anomaly, or opportunity clue.
- It has at least one entity or keyword that can be tracked.

### Watching

Move `new -> watching` when:

- The signal is relevant enough to track.
- The system has generated tracking queries.
- It has not yet reached spreading or validation thresholds.

### Spreading

Move to `spreading` when any condition is met:

- Evidence count increases by at least 3 within a short window.
- Distinct source count increases by at least 2.
- Social/trend sources show repeated appearances.
- Heat score crosses the configured threshold.

### Validating

Move to `validating` when:

- New evidence comes from higher-trust sources.
- Evidence includes primary-source material such as official posts, job pages, repositories, filings, or direct statements.
- Credibility score rises materially.

### Cooling

Move to `cooling` when:

- Heat score declines for multiple snapshots.
- No high-quality new evidence appears after initial spread.
- Discussion continues but becomes repetitive.

### Dormant

Move to `dormant` when:

- No meaningful evidence appears for the configured dormancy period.
- Default MVP dormancy period: 14 days.
- High-priority files may use 30 days.

### Resurrected

Move to `resurrected` when:

- Current state is `dormant` or `archived`.
- New evidence appears after the dormancy threshold.
- Evidence is not a duplicate and not low-quality repetition.

This is one of the most important product events.

### Verified

Move to `verified` when:

- The central claim is confirmed by an official, primary, or multiple independent reliable sources.
- Contradictions are resolved.
- Credibility score crosses the verification threshold.

### Debunked

Move to `debunked` when:

- Strong evidence disproves the main claim.
- The original source retracts or corrects the claim.
- Multiple credible sources show the signal was false or misleading.

### Noise

Move to `noise` when:

- The item is promotional spam or low-signal chatter.
- Similar claims repeat without new evidence.
- Source trust is low and no corroboration appears.
- Risk score is high and opportunity score is low.

## Same-File Matching Criteria

Evidence may attach to an existing intel file when enough of these match:

- Same primary entity.
- Same claim or thesis.
- Same product/project/topic.
- Overlapping keywords.
- Temporal proximity.
- Compatible signal type.
- New item is a follow-up, confirmation, contradiction, or extension.

The MVP should use conservative matching. If uncertain, suggest a match instead of auto-attaching.

## First-Seen Rule

`first_seen_at` should represent the earliest known evidence timestamp. It should not be overwritten casually.

If older evidence is later discovered, the system may update `first_seen_at` only by creating a clear `first_seen_corrected` event.

## Meaningful Evidence Rule

Not all new mentions are meaningful. Meaningful evidence should add at least one of:

- New source.
- New entity.
- New claim detail.
- Primary-source evidence.
- Stronger credibility.
- Contradiction or correction.
- New timing or location.
- New opportunity or risk implication.

## Alert Rules

The MVP should alert on:

- `dormant -> resurrected`
- `watching/new -> spreading`
- credibility score increases by at least 2 points
- opportunity score crosses 7
- risk score crosses 7
- state changes to `verified` or `debunked`

## Lifecycle Output

Every lifecycle evaluation should produce:

```json
{
  "previous_status": "dormant",
  "next_status": "resurrected",
  "reason": "New primary-source evidence appeared after 19 days of inactivity.",
  "evidence_ids": [123],
  "score_changes": {
    "heat_score": [1.2, 6.8],
    "credibility_score": [4.0, 6.5]
  }
}
```
