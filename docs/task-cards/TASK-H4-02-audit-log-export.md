# TASK-H4-02: Audit Log Export

## Goal

Let staging operators export workspace audit events for review and incident handoff.

## Scope

- Add CSV export for workspace audit events.
- Require workspace admin access in production.
- Add Workspace page export action that sends the current user token.

## Acceptance

- Admins can download workspace audit events as CSV.
- CSV includes timestamp, actor, action, target, and metadata.
- Export works with production token headers.
- Frontend type-check and build pass.

## Validation

```powershell
pytest backend\tests\test_workspace_members.py
npm run type-check
npm run build
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
