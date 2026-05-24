# AI START HERE

You are an external AI implementation agent working on Signal Tracker.

Your job is to continue the current product-hardening track. Do not restart from the old scaffold milestone.

## Current Status

P0-P4 are complete.

Start with:

- Task: the assignment in `NEXT_TASK.md`
- Task card: the matching file under `docs/task-cards/`
- Change package: the matching folder under `openspec/changes/`

## Required Reading

Read these files in order:

1. `AGENTS.md`
2. `SKILLS.md`
3. `TASKS.md`
4. `REVIEW.md`
5. `NEXT_TASK.md`
6. The task card named by `NEXT_TASK.md`
7. The matching OpenSpec proposal/design/tasks
8. `docs/architecture/system-architecture.md`
9. `docs/specs/acceptance-gates.md`
10. `docs/runbooks/local-dev.md`

Do not read the whole repo unless blocked.

## Implementation Goal

Continue from the current finished product surface:

- FastAPI backend with workspace-scoped signal tracking.
- Next.js frontend workbench.
- PostgreSQL migrations through P4 usage controls.
- Redis/Celery worker loop.
- Reports, notifications, usage limits, and team collaboration.
- H1 production configuration guardrails.

## Default Stack

Use this stack unless you have a strong reason to stop and ask:

- Backend: FastAPI + Pydantic.
- Database: PostgreSQL + SQLAlchemy + Alembic.
- Worker: Celery + Redis.
- Frontend: Next.js + React + TypeScript + Tailwind CSS.
- Tests: Pytest for backend, TypeScript type-check/build for frontend.

## Hard Boundaries

Do not restart completed P0-P4 tasks. Build only the current `NEXT_TASK.md` assignment.

## Expected Output

When done, return:

```text
Changed:
Verified:
Risks:
Next:
```

Update when relevant:

- `TASKS.md` status for the current task.
- `REVIEW.md` if there are blockers or follow-up risks.

## Validation

Run whatever commands are appropriate for the scaffold. The target validation shape is:

```powershell
docker compose up -d db redis
cd backend
python -m pytest tests/ -q
cd ..\apps\web
npm run type-check
npm run build
```

If a command cannot run, document why and what remains.

## Non-Negotiable Product Anchor

Signal Tracker is not a generic news reader.

The future primary object is `IntelFile`, and the product loop is:

```text
Discover signal
  -> Create intel file
  -> Attach evidence
  -> Track lifecycle
  -> Score opportunity/risk
  -> Alert and brief
```

This repository already has the foundation and commercial MVP slices. Current work should harden the product toward staging readiness.
