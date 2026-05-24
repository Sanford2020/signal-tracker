# Hosted Staging Readiness Review — 2026-05-24

## Verdict

`READY_FOR_RENDER_BLUEPRINT_DEPLOY`

Signal Tracker is ready for the owner to create a Render Blueprint deployment from the repository.

## Completed

- Render selected as the first hosted staging target.
- `render.yaml` added for API, worker, web, Postgres, and Redis-compatible Key Value.
- Render staging runbook added.
- Production bootstrap/admin operations require `ADMIN_API_KEY` and `X-Admin-Secret`.
- Remote hosted smoke test script added.
- Local release validation passes.

## Validation Evidence

Passed:

```powershell
pytest backend\tests\test_config.py -q
# 6 passed

pytest backend\tests\test_config.py backend\tests\test_admin_guard.py -q
# 8 passed

powershell -NoProfile -Command '<PowerShell parser check for scripts>'
# parsed validate-release, backup-postgres, restore-postgres, smoke-staging

python -c '<parse render.yaml>'
# parsed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 127 passed
# frontend type-check passed
# frontend build passed
```

## Owner Action Required

The next step requires access to external accounts:

1. Push this repository to GitHub.
2. Create a Render Blueprint from `render.yaml`.
3. Fill manual secrets:
   - `ALLOWED_ORIGINS`
   - `NEXT_PUBLIC_API_BASE_URL`
   - `ADMIN_API_KEY`
   - optional future AI provider secrets
4. Run migrations on the hosted database.
5. Run `scripts/smoke-staging.ps1` against the real hosted URLs.

## Remaining Production Gaps

- Replace staging secret guard with real user authentication before customer production.
- Configure hosted backup automation and restore drill.
- Configure external uptime/error monitoring.
- Decide live AI/source provider budget limits.
