# TASK-H4-01: Admin Audit Log

## Goal

Record security-sensitive workspace/admin actions for staging and future production operations.

## Scope

- Add `audit_events` storage.
- Record workspace bootstrap and workspace member upsert actions.
- Add workspace audit event list API.
- Show recent audit events on the Workspace page.

## Acceptance

- Bootstrap writes an audit event.
- Adding/updating a member writes an audit event.
- Workspace admins can list audit events.
- Frontend shows audit events for the selected workspace.

## Validation

```powershell
pytest backend\tests\test_workspace_members.py
alembic upgrade head
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
