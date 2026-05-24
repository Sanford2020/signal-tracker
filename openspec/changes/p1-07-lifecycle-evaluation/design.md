# Design: P1-07 Lifecycle Evaluation V1

## Evaluation flow

```text
POST /intel-files/{id}/evaluate
  -> load file + evidence
  -> apply deterministic rules
  -> LifecycleSnapshot (always)
  -> IntelEvent status_changed (when status changes)
  -> update IntelFile.status
```

## Rule priority

1. Terminal unchanged: verified, debunked, noise stay unless explicitly overridden later.
2. debunked: contradiction/correction evidence or high risk + low credibility.
3. verified: credibility >= 8 with corroboration or >= 3 evidence items.
4. noise: low opportunity + high risk, or noise evidence attached.
5. resurrected: dormant/archived with recent meaningful activity.
6. dormant: inactive longer than configured dormancy threshold.
7. spreading: evidence >= 3, sources >= 2, or heat >= 5.
8. validating: credibility >= 6 with corroboration or multiple evidence.
9. watching: new file with trackable entities/keywords.
10. no change.

## Dormancy

Configurable via `LIFECYCLE_DORMANCY_DAYS` (default 14).
