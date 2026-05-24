# TASK-H1-02: Deployment Runbook and Release Checklist

## Goal

Create a repeatable staging release package for AI employees and human operators.

## Scope

- Document deployment prerequisites and environment variables.
- Define migration, smoke-test, rollback, and release verification steps.
- Add one command that runs the release validation suite.
- Refresh AI handoff prompts so the next agent starts from the current post-P4/H1 state.

## Acceptance

- A deployment runbook exists under `docs/runbooks/`.
- A release checklist exists under `docs/runbooks/`.
- A validation script exists under `scripts/`.
- `AI_START_HERE.md` and `EXTERNAL_AI_PROMPT.md` point to the current task track.

## Validation

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
