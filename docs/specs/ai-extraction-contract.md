# AI Extraction Contract

## Purpose

The extraction step turns a `RawItem` into structured `SignalAnalysis`.

AI may help interpret text, but it must return strict JSON and must not directly mutate lifecycle state.

## Prompt Name

`signal_extract_v1`

## Input

```json
{
  "title": "Raw title",
  "url": "https://example.com",
  "content": "Raw content or pasted text",
  "source": {
    "name": "Manual",
    "source_type": "manual",
    "trust_tier": 2
  },
  "captured_at": "2026-05-23T00:00:00Z"
}
```

## Required Output

```json
{
  "summary": "2-3 sentence factual summary.",
  "signal_type": "hiring",
  "entities": [
    {
      "name": "Example AI",
      "type": "org"
    }
  ],
  "keywords": ["Example AI", "AI hardware", "supply chain hiring"],
  "claims": [
    {
      "text": "Example AI appears to be hiring for hardware supply chain roles.",
      "claim_type": "inference",
      "confidence": 0.62
    }
  ],
  "suggested_tracking_queries": [
    "Example AI hardware hiring",
    "Example AI supply chain role"
  ],
  "novelty_score": 7.0,
  "relevance_score": 8.0,
  "credibility_hint": 5.5,
  "risk_hint": 2.0,
  "opportunity_types": ["product", "startup", "technical"],
  "rationale": "This is an early hiring signal tied to a possible product direction.",
  "language": "en"
}
```

## Enums

### `signal_type`

- `hiring`
- `product`
- `github`
- `funding`
- `policy`
- `research`
- `market`
- `rumor`
- `incident`
- `community`
- `partnership`
- `other`

### Entity `type`

- `person`
- `org`
- `product`
- `project`
- `topic`
- `country`
- `event`
- `source`
- `other`

### Claim `claim_type`

- `fact`
- `inference`
- `rumor`
- `prediction`
- `contradiction`
- `correction`

### `opportunity_types`

- `product`
- `startup`
- `investment_clue`
- `content`
- `technical`
- `policy_compliance`
- `career`
- `none`

## Validation Rules

- Scores must be numbers from 0 to 10.
- `summary` must not be empty.
- `entities`, `keywords`, `claims`, and `suggested_tracking_queries` must be arrays.
- Unknown enum values should normalize to `other`.
- If output is invalid, store raw output and return a clear extraction error.

## Mock Mode

Mock mode must be deterministic for tests.

Given a raw item with title:

```text
Example AI hiring hardware supply chain lead
```

Mock output should include:

- `signal_type = hiring`
- entity `Example AI`
- keyword `hardware`
- novelty >= 6
- credibility_hint between 4 and 7

## AI Safety Rule

The AI may suggest:

- signal type
- scores
- tracking queries
- rationale

The deterministic backend must decide:

- whether to create an `IntelFile`
- whether evidence matches a file
- lifecycle status
- alerts
