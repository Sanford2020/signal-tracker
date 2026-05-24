# TASK-H4-05: Admin Rate Limit

## Goal

Protect public staging admin/bootstrap operations from basic brute-force attempts.

## Scope

- Add configurable admin rate limit setting.
- Add in-memory fixed-window limiter for single-instance staging.
- Apply limiter to `/api/v1/auth/bootstrap` in production.
- Document the single-instance limitation.

## Acceptance

- Production bootstrap is rate limited.
- Local development is not disrupted.
- Limit is configurable through env.
- Backend tests cover 429 behavior.

## Validation

```powershell
pytest backend\tests\test_admin_guard.py
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
