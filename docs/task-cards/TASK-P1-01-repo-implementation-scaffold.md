# TASK-P1-01: Repo Implementation Scaffold

## Owner Skill

Backend + Frontend + Deployment

## Goal

Create a runnable application scaffold for Signal Tracker.

## Dependencies

- P0 Review approved.

## Owned Files

Suggested, if using recommended stack:

- `backend/**`
- `apps/web/**`
- `docker/**`
- `docker-compose.yml`
- `.env.example`
- `scripts/**`
- package and config files

## Avoid

- Do not implement full product features.
- Do not design final UI polish.
- Do not add advanced crawlers, auth, billing, or vector search.

## Required Architecture

Recommended stack:

- FastAPI backend.
- PostgreSQL database.
- Redis worker broker.
- Celery or equivalent worker.
- Next.js frontend.
- Mock AI mode available from day one.

## Acceptance Criteria

- Backend starts locally.
- `GET /api/v1/health` returns success.
- Frontend starts locally and shows a simple Signal Tracker shell.
- Database migration framework exists.
- Worker process can start and register at least one example task.
- Test commands exist for backend and frontend.
- README or docs include local startup commands.

## Validation

Expected commands, adjust to chosen stack:

```powershell
docker compose up -d db redis
cd backend
python -m pytest tests/ -q
cd ..\apps\web
npm run type-check
npm run build
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
