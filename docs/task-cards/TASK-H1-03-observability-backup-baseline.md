# TASK-H1-03: Observability and Backup Baseline

## Goal

Add the minimum operational baseline needed before staging: request traceability, simple runtime logging, and documented database backup/restore.

## Scope

- Add structured request logs with request id, method, path, status, and duration.
- Return `X-Request-Id` on API responses.
- Add Postgres backup and restore helper scripts.
- Document backup, restore, and operational health checks.

## Acceptance

- API responses include `X-Request-Id`.
- Request logs are structured JSON lines.
- Backup and restore scripts exist under `scripts/`.
- Backup artifacts are ignored by git.
- Runbooks explain backup, restore, and basic operational checks.

## Validation

```powershell
pytest backend\tests\test_health.py backend\tests\test_config.py
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
