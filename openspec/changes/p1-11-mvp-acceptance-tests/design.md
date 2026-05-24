# Design: P1-11 MVP Acceptance Tests

## Scenario

```text
submit raw signal
  -> analyze
  -> create intel file
  -> score
  -> mark dormant in fixture
  -> attach follow-up evidence
  -> evaluate lifecycle
  -> alert created
  -> daily briefing includes resurrected file
```

## Boundary

No new product behavior. Use existing API routes and direct fixture state only where required by the task card.
