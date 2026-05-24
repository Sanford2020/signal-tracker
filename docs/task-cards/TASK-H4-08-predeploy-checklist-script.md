# TASK-H4-08: Predeploy Checklist Script

## Goal

Provide one local command that runs the deployment preflight checks before hosted staging deploy.

## Scope

- Parse PowerShell helper scripts.
- Run env readiness check.
- Run release validation.
- Document usage in deployment runbook.

## Acceptance

- `scripts/predeploy-check.ps1` exists.
- Script fails if env readiness fails.
- Script fails if release validation fails.
- Script is documented.

## Validation

```powershell
powershell -NoProfile -Command '<PowerShell parser check>'
powershell -ExecutionPolicy Bypass -File scripts\predeploy-check.ps1 -EnvFile tmp.env.production -Mode production
```
