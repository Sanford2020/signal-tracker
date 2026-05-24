# TASK-H4-03: Security Response Headers

## Goal

Add baseline security headers for hosted staging and future production.

## Scope

- Add `X-Content-Type-Options`.
- Add `X-Frame-Options`.
- Add `Referrer-Policy`.
- Add `Permissions-Policy`.
- Add `Cache-Control: no-store` for API responses.

## Acceptance

- Health/API responses include security headers.
- Existing API behavior remains unchanged.

## Validation

```powershell
pytest backend\tests\test_health.py
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
