# TASK-H2-02: Staging Auth Guard

## Goal

Prevent public staging deployments from exposing bootstrap/admin-style operations without an explicit secret.

## Scope

- Add `ADMIN_API_KEY` configuration.
- Require `ADMIN_API_KEY` in production settings.
- Require `X-Admin-Secret` for `/api/v1/auth/bootstrap` when `APP_ENV=production`.
- Keep local development unchanged.
- Update Render environment documentation and validation tests.

## Acceptance

- Local bootstrap still works without a secret.
- Production settings fail fast without `ADMIN_API_KEY`.
- Production bootstrap returns `401` without `X-Admin-Secret`.
- Production bootstrap succeeds with the correct `X-Admin-Secret`.
- Render Blueprint marks `ADMIN_API_KEY` as a manual secret.

## Validation

```powershell
pytest backend\tests\test_config.py backend\tests\test_admin_guard.py
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
