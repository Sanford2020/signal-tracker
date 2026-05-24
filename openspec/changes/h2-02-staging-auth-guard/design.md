# Design

## Guard

`ADMIN_API_KEY` is configured through settings.

When `APP_ENV=production`:

- settings validation requires `ADMIN_API_KEY`
- `/api/v1/auth/bootstrap` requires `X-Admin-Secret`
- the provided header is compared with `secrets.compare_digest`

When not in production, local development keeps the existing bootstrap flow.

## Boundary

This is not full user authentication. It is a staging guard for dangerous initialization operations. Production-grade auth remains a separate task.
