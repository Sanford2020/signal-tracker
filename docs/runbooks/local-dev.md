# Local Development

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop

## Quick Start

```powershell
# 1. Copy environment
Copy-Item .env.example .env

# 2. Start infrastructure
docker compose up -d db redis

# 3. Backend
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# 4. Frontend (new terminal)
cd apps/web
npm install
npm run dev

# 5. Worker (optional, new terminal)
cd <repo-root>
$env:PYTHONPATH = "backend;."
celery -A workers.celery_app worker --loglevel=info --pool=solo
```

## Validation

```powershell
docker compose up -d db redis
cd backend
python -m pytest tests/ -q
cd ..\apps\web
npm run type-check
npm run build
```

## Migrations

```powershell
cd backend
alembic upgrade head
```

## Health Check

```powershell
curl http://localhost:8000/api/v1/health
```

Expected fields:

```json
{
  "status": "ok",
  "service": "Signal Tracker API",
  "environment": "development",
  "version": "0.1.0"
}
```

## Production Configuration Baseline

For production-like environments:

- Set `APP_ENV=production`.
- Set `DATABASE_URL` to a non-local database credential.
- Set `ALLOWED_ORIGINS` to explicit trusted frontend origins.
- Do not use `*` for CORS origins.
- Keep `AI_EXTRACTION_MODE=mock` until a real provider key, model, and budget policy are configured.

The backend fails startup validation in production mode if default local database credentials or wildcard origins are used.

## Troubleshooting

### `alembic` fails with password authentication for `signal_tracker`

1. Ensure project Postgres is running: `docker compose up -d db redis`
2. Copy env: `Copy-Item .env.example .env`
3. If port 5432 is already used by another Postgres instance, change `POSTGRES_PORT` and `DATABASE_URL` in `.env`

Alembic requires a live database connection; backend pytest does not.
