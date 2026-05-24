# NEXT_TASK.md

## Assignment

Owner action: deploy Render Blueprint and run hosted smoke test.

## Current Status

- `TASK-P4-05: Usage Limits and Cost Controls` is approved.
- P4 Commercialization slice is complete.
- `TASK-H1-01: Production Config and Security Baseline` is implemented and validated.
- `TASK-H1-02: Deployment Runbook and Release Checklist` is implemented and validated.
- `TASK-H1-03: Observability and Backup Baseline` is implemented and validated.
- `TASK-H1-04: Staging Readiness Review` is complete.
- `TASK-H2-01: Hosted Staging Target and Deployment Adapter` is implemented and validated.
- `TASK-H2-02: Staging Auth Guard` is implemented and validated.
- `TASK-H2-03: Hosted Staging Smoke Test Script` is implemented and validated.
- `TASK-H2-04: Hosted Staging Readiness Review` is complete.
- `TASK-H3-01: Workspace Membership Guard` is implemented and validated.
- `TASK-H3-02: Workspace Member Management` is implemented and validated.
- `TASK-H3-03: Staging User Access Token` is implemented and validated.
- `TASK-H3-04: Access Control Readiness Review` is complete.
- `TASK-H4-01: Admin Audit Log` is implemented and validated.
- `TASK-H4-02: Audit Log Export` is implemented and validated.
- `TASK-H4-03: Security Response Headers` is implemented and validated.
- `TASK-H4-04: Environment Readiness Check` is implemented and validated.
- `TASK-H4-05: Admin Rate Limit` is implemented and validated.
- `TASK-H4-06: Runtime Readiness Endpoint` is implemented and validated.
- `TASK-H4-07: Production Env Template` is implemented and validated.
- `TASK-H4-08: Predeploy Checklist Script` is implemented and validated.
- H5 gap closure is implemented and validated:
  - GitHub Releases source provider added as the first real provider.
  - Celery Beat now schedules source checks, lifecycle dormancy/resurrection, and notification delivery.
  - Homepage scaffold replaced with a working dashboard.
  - REVIEW status updated.
  - Stale temporary SQLite artifact removed.

## Goal

Create the real hosted staging deployment using the prepared Render Blueprint, access-control baseline, audit log/export, security headers, readiness endpoint, rate limit, env preflight, predeploy script, real GitHub Releases provider, and scheduled worker loop.

## Validation

- Push repository to GitHub.
- Push repository to GitLab.
- Create Render Blueprint from `render.yaml`.
- Fill manual secrets and hosted URLs.
- Create `.env.production` from `.env.production.example`.
- Run `scripts\predeploy-check.ps1`.
- Run `scripts\check-env-readiness.ps1` against the production-like env file.
- Run migrations through `0013_audit_events`.
- Run `scripts\smoke-staging.ps1` against hosted URLs with `-AdminApiKey`.

## Next Implementation Candidates After Staging

- Add RSS/Hacker News provider pack for AI market and product signals.
- Build source operations UI for provider health, run history, and match suggestion triage.
- Add saved filters and sorting to the Intel Files workbench.
