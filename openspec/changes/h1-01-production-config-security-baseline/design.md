# Design

## Runtime Settings

The backend owns deployment configuration through `Settings`.

- `APP_VERSION` identifies the running build.
- `ALLOWED_ORIGINS` is stored as a string for environment compatibility and parsed into `allowed_origin_list` for FastAPI CORS.
- `DATABASE_URL` remains the backend database contract.

## Production Guardrails

When `APP_ENV=production`, settings validation rejects:

- the default local `signal_tracker:signal_tracker` database credentials
- empty or wildcard CORS origins

This is intentionally a startup-time failure. A misconfigured production deployment should fail fast before accepting traffic.

## Compose Contract

`docker-compose.yml` remains local-first, but database credentials and ports now read from environment variables with local defaults. This keeps the same developer workflow while making the template clearer for staging and hosted deployments.
