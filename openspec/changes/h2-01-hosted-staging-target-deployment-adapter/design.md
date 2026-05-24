# Design

## Decision Criteria

Evaluate targets by:

- support for FastAPI backend
- support for long-running Celery worker
- managed Postgres availability
- managed Redis availability
- secret management
- migration workflow
- frontend deployment fit
- cost and operational simplicity

## Expected Output

Add one platform-specific deployment path under `docs/runbooks/` and update `docs/reviews/staging-readiness-2026-05-24.md` only if the readiness verdict changes.

Config files are optional. Prefer documentation first unless the chosen platform has a simple, stable config format.
