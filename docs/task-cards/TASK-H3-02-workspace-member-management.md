# TASK-H3-02: Workspace Member Management

## Goal

Allow staging operators to manage workspace collaborators without editing the database directly.

## Scope

- Add workspace member list API.
- Add workspace member create/update API.
- Restrict member creation to workspace admins in production mode.
- Add Workspace page member list and add-member form.

## Acceptance

- Admins can add workspace members.
- Members can list workspace members.
- Non-admin members cannot add members in production.
- Frontend can list and add members from the Workspace page.

## Validation

```powershell
pytest backend\tests\test_workspace_members.py
npm run type-check
npm run build
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
