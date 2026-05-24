# TASK-H4-06: Runtime Readiness Endpoint

## Goal

Expose a readiness endpoint that confirms the API can reach the database.

## Scope

- Add `GET /api/v1/ready`.
- Execute a simple database probe.
- Return `503` when database readiness fails.
- Keep `GET /api/v1/health` as lightweight process health.

## Acceptance

- `/health` remains lightweight.
- `/ready` returns database readiness.
- Backend tests cover readiness.

## Validation

```powershell
pytest backend\tests\test_health.py
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
