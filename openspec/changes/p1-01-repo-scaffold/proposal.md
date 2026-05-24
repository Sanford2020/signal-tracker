# Proposal: P1-01 Repo Implementation Scaffold

## Intent

Create the runnable implementation foundation for Signal Tracker so AI employees can begin feature work against a real app structure.

## Problem

The project currently has planning, specs, task cards, and architecture docs, but no runnable backend, frontend, database, worker, or test skeleton.

Feature implementation should not begin until there is a stable scaffold.

## Scope

In scope:

- Backend application skeleton.
- Frontend application skeleton.
- Database and migration setup.
- Worker skeleton.
- Local development commands.
- Initial health route.
- Initial test commands.

Out of scope:

- Manual signal submission.
- Core domain models.
- AI extraction.
- Lifecycle and scoring.
- Authentication.
- Billing.
- Automated crawlers.
- UI polish.

## Approach

Use the default architecture unless the Master Agent changes it:

- FastAPI backend.
- Next.js frontend.
- PostgreSQL.
- Redis.
- Celery or equivalent worker.
- Pytest and TypeScript validation.

The scaffold should be minimal but real. It should make later tasks easy to implement without reshaping the repo.

## Success

The stack can boot locally and exposes a backend health endpoint plus a frontend shell.
