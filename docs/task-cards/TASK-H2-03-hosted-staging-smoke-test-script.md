# TASK-H2-03: Hosted Staging Smoke Test Script

## Goal

Add a one-command smoke test for hosted staging deployments.

## Scope

- Validate backend health response.
- Validate `X-Request-Id` response header.
- Validate production bootstrap guard behavior.
- Optionally validate frontend URL.
- Document usage in the Render staging runbook.

## Acceptance

- `scripts/smoke-staging.ps1` exists.
- Script requires `ApiBaseUrl`.
- Script can optionally check `WebBaseUrl`.
- Script checks bootstrap returns `401` without `X-Admin-Secret`.
- Script can optionally verify bootstrap with `AdminApiKey`.

## Validation

```powershell
powershell -NoProfile -Command '<PowerShell parser check>'
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
