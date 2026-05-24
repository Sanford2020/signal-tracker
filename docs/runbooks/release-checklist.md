# Release Checklist

## Scope Lock

- [ ] Confirm the release task in `TASKS.md`.
- [ ] Confirm `NEXT_TASK.md` matches the work being shipped.
- [ ] Confirm no unrelated local changes are mixed into the release.

## Configuration

- [ ] `.env.example` contains all required non-secret keys.
- [ ] Staging secrets are stored outside the repository.
- [ ] `APP_ENV=production` is set for production-like deploys.
- [ ] `DATABASE_URL` uses non-default credentials.
- [ ] `ALLOWED_ORIGINS` lists explicit trusted origins.
- [ ] `ADMIN_API_KEY` is set for production-like deploys.
- [ ] Workspace operator access tokens are stored outside the repository.
- [ ] `NEXT_PUBLIC_API_BASE_URL` points to the target backend.

## Database

- [ ] Postgres is reachable.
- [ ] Backup exists before migration.
- [ ] Backup path is recorded and stored outside git.
- [ ] `alembic upgrade head` succeeds.
- [ ] Migration head is recorded in release notes.

## Validation

- [ ] `powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1` succeeds.
- [ ] Backend health check succeeds.
- [ ] `X-Request-Id` is returned on API responses.
- [ ] Frontend build succeeds.
- [ ] Product smoke path succeeds.

## Operations

- [ ] Worker starts and connects to Redis.
- [ ] Backend logs include structured request entries.
- [ ] Usage limits are set for the target plan.
- [ ] Notification channels are disabled or pointed at staging destinations unless production approval exists.
- [ ] Report export works for Markdown and PDF.

## Rollback

- [ ] Previous application artifact is available.
- [ ] Database backup restore path is known.
- [ ] Rollback owner is assigned.
- [ ] Rollback smoke test is documented.
