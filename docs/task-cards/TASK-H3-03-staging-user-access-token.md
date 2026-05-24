# TASK-H3-03: Staging User Access Token

## Goal

Prevent production workspace authorization from trusting a spoofable email header alone.

## Scope

- Generate access tokens for bootstrap users and newly added workspace members.
- Store only token hashes and short token hints.
- Require `X-User-Token` with `X-User-Email` for production workspace-scoped routes.
- Store the current user's token in frontend local storage.
- Return newly issued member tokens once so operators can share them during staging.

## Acceptance

- Production workspace routes reject missing user tokens.
- Production workspace routes allow valid workspace member email/token pairs.
- Tokens are not stored in plaintext.
- Local development remains compatible.
- Database migration adds token hash/hint columns.

## Validation

```powershell
pytest backend\tests\test_workspace_access_guard.py backend\tests\test_workspace_members.py
alembic upgrade head
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
