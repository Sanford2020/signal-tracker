# TASK-H3-01: Workspace Membership Guard

## Goal

Prevent hosted staging users from reading or mutating workspace-scoped data by guessing a workspace id.

## Scope

- Require workspace membership for workspace-scoped routes when `APP_ENV=production`.
- Keep local development compatibility.
- Apply guard to inbox, intel file, notification, usage, and source-check routes.
- Ensure intel file creation/evidence attachment cannot cross workspace boundaries when guarded.

## Acceptance

- Production workspace-scoped routes require `X-User-Email`.
- Production workspace-scoped routes reject non-members.
- Production workspace-scoped routes allow members.
- Local tests continue to pass.

## Validation

```powershell
pytest backend\tests\test_workspace_access_guard.py backend\tests\test_auth_workspaces.py
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
