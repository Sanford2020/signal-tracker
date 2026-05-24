# Design: P2-02 Scheduled Source Checks

## Flow

```text
POST /api/v1/source-checks/run
  -> load enabled tracking queries up to limit
  -> checker.search(query)
  -> SourceCheckRun
  -> SourceCheckResult rows
```

## Checker

The service uses a checker protocol so tests can inject a fake checker. Default checker is a no-network stub.

## Boundary

Source check results are candidates only. P2-03 decides whether they match existing IntelFiles.
