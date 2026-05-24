# Observability and Backup Runbook

## Request Logs

The backend emits one structured JSON log line per request.

Fields:

- `event`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

Clients can pass `X-Request-Id`; otherwise the backend generates one and returns it in the response header.

## Log Level

Use `LOG_LEVEL` to control backend verbosity.

Recommended baseline:

```text
LOG_LEVEL=INFO
```

## Operator Checks

Daily staging checks:

1. Open `/api/v1/health`.
2. Confirm the response has the expected `environment`, `version`, and `X-Request-Id`.
3. Review backend logs for repeated `request_failed` events.
4. Confirm worker process is running.
5. Confirm Redis and Postgres health checks are passing.
6. Run one product smoke path from the deployment runbook.

## Backup

Create a local Postgres dump from the Compose database:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup-postgres.ps1
```

Backups are written to `backups/` and ignored by git.

## Restore

Restore a backup into the Compose database:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\restore-postgres.ps1 -BackupFile backups\signal-tracker-YYYYMMDD-HHMMSS.dump
```

Restore is destructive for the target database. Use it only after confirming the target environment and backup file.

## Staging Backup Policy

- Backup before every migration.
- Keep at least the latest 7 daily backups for staging.
- Keep the latest verified backup path in release notes.
- Test restore at least once before treating staging as reliable.
