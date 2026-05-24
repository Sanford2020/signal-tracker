# External AI Prompt

Use this prompt with another AI coding tool when continuing implementation.

```text
You are an external AI implementation agent working in:

C:\Users\sanford\Desktop\ai_code_new\signal-tracker

Start with the task named in `NEXT_TASK.md`. Do not restart completed P0-P4 work.

Read these files in order:

1. AGENTS.md
2. SKILLS.md
3. TASKS.md
4. REVIEW.md
5. AI_START_HERE.md
6. NEXT_TASK.md
7. The matching task card under docs/task-cards/
8. The matching OpenSpec proposal/design/tasks under openspec/changes/
9. docs/architecture/system-architecture.md
10. docs/specs/acceptance-gates.md
11. docs/runbooks/local-dev.md
12. docs/reviews/staging-readiness-2026-05-24.md

Goal:
Continue the current product-hardening track after P0-P4:
- preserve existing product behavior
- implement only the current task assignment
- update task card/OpenSpec/docs when the contract changes
- validate backend, frontend, and release checks as applicable

Default stack:
- FastAPI + Pydantic
- PostgreSQL + SQLAlchemy + Alembic
- Celery + Redis
- Next.js + React + TypeScript + Tailwind
- Pytest and frontend type-check/build

Hard boundaries:
- Do not restart completed milestones.
- Do not turn this into a generic news dashboard.
- Do not mix unrelated refactors into the task.
- Do not commit secrets.

Validation target:
- docker compose up -d db redis
- cd backend && python -m pytest tests/ -q
- cd apps/web && npm run type-check && npm run build
- powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1

When finished, update TASKS.md and return:

Changed:
Verified:
Risks:
Next:
```
