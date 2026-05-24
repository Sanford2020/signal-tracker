# TASK-H4-04: Environment Readiness Check

## Goal

Catch missing or unsafe staging/production environment values before deployment.

## Scope

- Add a local PowerShell env readiness script.
- Validate required backend/frontend env keys.
- Detect default local database credentials in production.
- Detect unsafe origins and local frontend API URLs.
- Document usage in deployment runbooks.

## Acceptance

- Script can check a provided env file.
- Production mode requires `ADMIN_API_KEY`.
- Production mode rejects local/default values.
- Script parser validation passes.

## Validation

```powershell
powershell -NoProfile -Command '<PowerShell parser check>'
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
