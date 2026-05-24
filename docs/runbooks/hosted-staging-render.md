# Hosted Staging Runbook: Render

## Decision

Default hosted staging target: Render.

Reason: Signal Tracker currently needs a Python web API, a long-running Celery worker, Postgres, Redis-compatible queue storage, and a Node/Next.js frontend. Render supports these pieces in one Blueprint-style deployment, which keeps the first hosted staging run simpler than splitting frontend, backend, worker, database, and queue across multiple providers.

Official references used for this decision:

- Render FastAPI deployment: https://render.com/docs/deploy-fastapi
- Render Background Workers: https://render.com/docs/background-workers
- Render Celery quickstart: https://render.com/docs/deploy-celery
- Render Blueprint reference: https://render.com/docs/blueprint-spec
- Render Key Value: https://render.com/redis

## Target Architecture

```text
Render Blueprint
  -> signal-tracker-api      FastAPI web service
  -> signal-tracker-worker   Celery background worker
  -> signal-tracker-web      Next.js web service
  -> signal-tracker-db       Render Postgres
  -> signal-tracker-redis    Render Key Value, Redis-compatible
```

## Files

- `render.yaml`: Render Blueprint.
- `docs/runbooks/deployment.md`: general deployment runbook.
- `docs/runbooks/release-checklist.md`: release gate.
- `docs/runbooks/observability-backup.md`: request tracing and backup baseline.

## Required Manual Values

Render should prompt for values marked `sync: false` in `render.yaml`.

Set:

```text
ALLOWED_ORIGINS=https://<signal-tracker-web>.onrender.com
NEXT_PUBLIC_API_BASE_URL=https://<signal-tracker-api>.onrender.com
ADMIN_API_KEY=<long-random-secret>
ADMIN_RATE_LIMIT_PER_MINUTE=30
AI_API_KEY=
AI_BASE_URL=
```

Keep `AI_EXTRACTION_MODE=mock` for the first staging deployment.

Before filling hosted secrets, validate a local production-like env file:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile ".env.production" -Mode production
```

Before creating the Blueprint, run the full predeploy check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\predeploy-check.ps1 -EnvFile ".env.production" -Mode production
```

Production-mode workspace requests require both:

```text
X-Workspace-Id=<workspace-id>
X-User-Email=<member-email>
X-User-Token=<member-access-token>
```

Tokens are issued once by bootstrap and member creation responses. Store them outside the repository.

Admin/bootstrap operations are protected by an in-memory per-instance rate limit. For multi-instance production, replace this with provider, proxy, or Redis-backed rate limiting.

## Create Staging

1. Push the repository to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Confirm `render.yaml` is detected.
4. Fill manual environment values.
5. Deploy `signal-tracker-db` and `signal-tracker-redis`.
6. Deploy `signal-tracker-api`.
7. Deploy `signal-tracker-worker`.
8. Deploy `signal-tracker-web`.

## Database Migration

Run after the API service has built and can connect to the database:

```bash
cd backend
alembic upgrade head
```

Use Render Shell or a one-off job attached to the API service environment.

## Smoke Test

Backend:

```bash
curl https://<signal-tracker-api>.onrender.com/api/v1/health
curl https://<signal-tracker-api>.onrender.com/api/v1/ready
```

Expected:

```json
{
  "status": "ok",
  "service": "Signal Tracker API",
  "environment": "production",
  "version": "0.1.0"
}
```

Confirm the response also includes `X-Request-Id`.

One-command remote smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-staging.ps1 `
  -ApiBaseUrl "https://<signal-tracker-api>.onrender.com" `
  -WebBaseUrl "https://<signal-tracker-web>.onrender.com"
```

After creating `ADMIN_API_KEY`, include it to verify guarded bootstrap:
This also verifies that the issued user access token can read workspace members.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-staging.ps1 `
  -ApiBaseUrl "https://<signal-tracker-api>.onrender.com" `
  -WebBaseUrl "https://<signal-tracker-web>.onrender.com" `
  -AdminApiKey "<ADMIN_API_KEY>"
```

Frontend:

1. Open `https://<signal-tracker-web>.onrender.com`.
2. Open `/workspace`.
3. Bootstrap or select a workspace.
4. Store the returned workspace id, user email, and access token.
5. Submit one inbox signal.
6. Run mock extraction.
7. Create an intel file.
8. Open daily briefing.

Worker:

1. Confirm `signal-tracker-worker` is running.
2. Confirm it connects to Render Key Value.
3. Run a source-check or lifecycle task from the app when available.

Bootstrap in production mode:

```bash
curl -X POST https://<signal-tracker-api>.onrender.com/api/v1/auth/bootstrap \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: <ADMIN_API_KEY>" \
  -d '{"email":"owner@example.com","name":"Owner","workspace_name":"Signal Tracker Staging"}'
```

## Rollback

1. Disable auto-deploy on the affected service if repeated deploys are failing.
2. Roll back to the previous successful Render deploy.
3. If a migration caused the issue, restore the latest verified Postgres backup.
4. Re-run health and product smoke tests.

## Known Gaps Before Production

- Production auth is still bootstrap/header-oriented and must be hardened.
- Hosted backup automation needs to be configured and restore-tested.
- External monitoring and alert routing are not configured.
- Live AI and source providers are intentionally disabled for first staging.
