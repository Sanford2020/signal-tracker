# TASK-H2-01: Hosted Staging Target and Deployment Adapter

## Goal

Choose the hosted staging deployment target and add the minimum platform-specific adapter or runbook needed to deploy Signal Tracker outside local Compose.

## Scope

- Compare feasible staging targets for this repo shape.
- Pick one default target unless the owner overrides it.
- Document backend, frontend, worker, Postgres, Redis, secrets, migrations, and smoke tests for that target.
- Add platform-specific config files only if they are low-risk and directly useful.

## Suggested Default

Use a pragmatic split unless a better target is selected:

- Frontend: Vercel
- Backend and worker: Render, Fly.io, or Railway
- Database: managed Postgres
- Redis: managed Redis

If a single-platform deployment is simpler for the selected target, prefer the simpler path.

## Avoid

- Do not commit secrets.
- Do not remove local Docker Compose support.
- Do not introduce Kubernetes unless explicitly required.
- Do not change product behavior while choosing deployment shape.

## Acceptance

- Target comparison is documented.
- One staging target is selected with rationale.
- Deployment runbook is updated with platform-specific steps.
- Required secrets and environment variables are listed.
- Migration and smoke-test commands are documented.
- Any added config passes local validation.

## Validation

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
