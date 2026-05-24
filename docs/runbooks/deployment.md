# Deployment Runbook

## Purpose

This runbook describes the first production-like deployment path for Signal Tracker after P4 and H1-01.

Target stage: staging first, then production after the same checklist passes with real secrets and operator approval.

## Required Services

- FastAPI backend
- Next.js frontend
- PostgreSQL 16+
- Redis 7+
- Celery worker

## Hosted Staging Target

The selected first hosted staging target is Render.

Use:

- `render.yaml` for the Blueprint.
- `docs/runbooks/hosted-staging-render.md` for platform-specific deployment steps.
- `docs/architecture/hosted-staging-targets.md` for target comparison and rationale.

## Required Environment

Backend:

```text
APP_ENV=production
APP_NAME=Signal Tracker API
APP_VERSION=<release-version>
API_V1_PREFIX=/api/v1
DATABASE_URL=<postgres-url-with-non-default-credentials>
REDIS_URL=<redis-url>
CELERY_BROKER_URL=<redis-url>
CELERY_RESULT_BACKEND=<redis-url-db-1>
ALLOWED_ORIGINS=<trusted-frontend-origin>
ADMIN_API_KEY=<long-random-secret>
ADMIN_RATE_LIMIT_PER_MINUTE=30
AI_EXTRACTION_MODE=mock
USAGE_AI_EXTRACTION_MONTHLY_LIMIT=10000
USAGE_SOURCE_CHECK_MONTHLY_LIMIT=100000
```

Frontend:

```text
NEXT_PUBLIC_API_BASE_URL=<backend-public-url>
```

## Preflight

1. Confirm `APP_ENV=production`.
2. Confirm `DATABASE_URL` does not use the local `signal_tracker:signal_tracker` credential.
3. Confirm `ALLOWED_ORIGINS` lists explicit frontend origins and does not use `*`.
4. Confirm `ADMIN_API_KEY` is set and stored outside the repository.
5. Confirm `ADMIN_RATE_LIMIT_PER_MINUTE` is set for public staging.
6. Confirm the database is reachable from the backend runtime.
7. Confirm Redis is reachable from the backend and worker runtimes.
8. Run release validation locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```

9. Check environment readiness:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile ".env.production" -Mode production
```

Use `.env.production.example` as a starting point, but replace every placeholder before running the readiness check.

Full predeploy check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\predeploy-check.ps1 -EnvFile ".env.production" -Mode production
```

## Deployment Steps

1. Build backend and frontend artifacts.
2. Apply database migrations:

```powershell
cd backend
alembic upgrade head
```

3. Start backend.
4. Start worker.
5. Start frontend.
6. Run smoke tests.
7. Create and record a database backup before any migration-driven release.

## Smoke Tests

Backend:

```powershell
curl <backend-url>/api/v1/health
curl <backend-url>/api/v1/ready
```

Expected fields:

```json
{
  "status": "ok",
  "service": "Signal Tracker API",
  "environment": "production",
  "version": "<release-version>"
}
```

Product smoke path:

1. Bootstrap or select a workspace.
2. Submit one manual signal.
3. Run extraction in mock mode.
4. Create an intel file.
5. Attach evidence or accept a match suggestion if available.
6. Open daily briefing.
7. Export the daily report as Markdown.

Hosted smoke script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-staging.ps1 -ApiBaseUrl "<backend-url>" -WebBaseUrl "<frontend-url>"
```

Operational smoke path:

1. Confirm `X-Request-Id` is returned by the health endpoint.
2. Confirm backend logs include a matching `request_completed` event.
3. Confirm a backup can be created in staging before migrations.

## Rollback

Use this order:

1. Stop new traffic to the frontend.
2. Stop backend and worker.
3. Restore the previous application version.
4. If the migration changed schema incompatibly, restore the latest verified database backup.
5. Start backend, worker, and frontend.
6. Re-run the health check and one product smoke path.

## Release Notes Template

```text
Release:
Date:
Environment:
Commit/build:
Database migration head:
Changed:
Validated:
Known risks:
Rollback plan:
Operator:
```
