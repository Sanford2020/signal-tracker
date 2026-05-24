# TASK-H4-07: Production Env Template

## Goal

Provide a production-like environment template and ensure readiness checks catch placeholder values.

## Scope

- Add `.env.production.example`.
- Add placeholder detection to env readiness checks.
- Document that the production template is not directly deployable until placeholders are replaced.

## Acceptance

- Production env template exists.
- Env readiness script rejects placeholder values.
- Positive production-like env check still passes.

## Validation

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile tmp.env.production -Mode production
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
