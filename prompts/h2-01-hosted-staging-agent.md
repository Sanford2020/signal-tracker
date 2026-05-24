# H2-01 Agent Prompt

You are an AI implementation agent working in:

```text
C:\Users\sanford\Desktop\ai_code_new\signal-tracker
```

Current state:

- P0-P4 are complete.
- H1 Product Hardening is complete.
- The project is ready for a local staging dry run, not public production.
- Your task is `TASK-H2-01: Hosted Staging Target and Deployment Adapter`.

Read these files first:

1. `AGENTS.md`
2. `TASKS.md`
3. `NEXT_TASK.md`
4. `docs/reviews/staging-readiness-2026-05-24.md`
5. `docs/task-cards/TASK-H2-01-hosted-staging-target-deployment-adapter.md`
6. `openspec/changes/h2-01-hosted-staging-target-deployment-adapter/proposal.md`
7. `openspec/changes/h2-01-hosted-staging-target-deployment-adapter/design.md`
8. `openspec/changes/h2-01-hosted-staging-target-deployment-adapter/tasks.md`
9. `docs/runbooks/deployment.md`
10. `docs/runbooks/release-checklist.md`
11. `docs/runbooks/observability-backup.md`

Goal:

- Compare hosted staging targets for this FastAPI + Next.js + Celery + Postgres + Redis app.
- Pick one default path unless the owner has specified a platform.
- Add platform-specific deployment instructions or minimal adapter config.
- Preserve local Docker Compose development.
- Run `powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1`.

Return:

```text
Changed:
Verified:
Risks:
Next:
```
