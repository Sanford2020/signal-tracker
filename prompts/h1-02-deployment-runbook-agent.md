# H1-02 Agent Prompt

You are an AI implementation agent working in:

```text
C:\Users\sanford\Desktop\ai_code_new\signal-tracker
```

Current state:

- P0-P4 are complete.
- H1-01 production config and security baseline is complete.
- Your task is `TASK-H1-02: Deployment Runbook and Release Checklist`.

Read these files first:

1. `AGENTS.md`
2. `TASKS.md`
3. `NEXT_TASK.md`
4. `docs/task-cards/TASK-H1-02-deployment-runbook-release-checklist.md`
5. `openspec/changes/h1-02-deployment-runbook-release-checklist/proposal.md`
6. `openspec/changes/h1-02-deployment-runbook-release-checklist/design.md`
7. `openspec/changes/h1-02-deployment-runbook-release-checklist/tasks.md`
8. `docs/runbooks/local-dev.md`
9. `docs/runbooks/deployment.md`
10. `docs/runbooks/release-checklist.md`

Goal:

- Verify the deployment runbook is complete enough for staging.
- Verify the release checklist covers config, database, validation, operations, and rollback.
- Run `powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1`.
- Update `TASKS.md`, `REVIEW.md`, and `NEXT_TASK.md` only if your validation finds a real follow-up.

Return:

```text
Changed:
Verified:
Risks:
Next:
```
