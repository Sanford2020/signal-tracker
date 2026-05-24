# Design

## Request Traceability

The FastAPI app installs one HTTP middleware that:

- accepts or generates `X-Request-Id`
- measures request duration
- writes a structured JSON log line
- returns `X-Request-Id` to the caller

The middleware intentionally avoids external dependencies.

## Backup Helpers

`scripts/backup-postgres.ps1` runs `pg_dump` inside the Compose Postgres container and writes a compressed custom-format dump under `backups/`.

`scripts/restore-postgres.ps1` streams a selected dump into `pg_restore` inside the Compose Postgres container.

## Boundaries

This is not a full monitoring stack. Metrics, dashboards, alert routing, and hosted backup automation are follow-up work.
