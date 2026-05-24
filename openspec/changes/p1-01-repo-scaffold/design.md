# Design: P1-01 Repo Implementation Scaffold

## Technical Approach

Create a conventional web application layout:

```text
backend/
  app/
    main.py
    api/
    core/
    db/
    models/
    modules/
  tests/
apps/
  web/
workers/
docker/
scripts/
```

## Backend

Backend should provide:

- FastAPI app factory or `app`.
- `/api/v1/health`.
- Config loading from environment.
- DB session module stub.
- Test setup.

## Frontend

Frontend should provide:

- Next.js app.
- Signal Tracker shell.
- Navigation placeholders:
  - Inbox
  - Intel Files
  - Briefing
  - Alerts
  - Sources

## Database

Database setup should include:

- PostgreSQL connection configuration.
- Migration framework.
- Empty initial migration or migration readiness.

## Worker

Worker setup should include:

- Queue configuration.
- Example task.
- Command to start worker locally.

## Docker / Local Dev

Provide local development support for:

- database
- redis
- backend
- frontend
- worker

## Design Decisions

### Decision: Keep Scaffold Feature-Light

This task should not implement product behavior. Its job is to reduce setup friction for later tasks.

### Decision: Mock-Friendly From Start

The app should be able to run without external AI credentials.

## Verification

Expected checks:

- Backend tests pass.
- Frontend type-check/build passes.
- Backend health route responds.
- Worker imports and starts.
