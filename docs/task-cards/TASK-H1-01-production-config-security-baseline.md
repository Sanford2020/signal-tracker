# TASK-H1-01: Production Config and Security Baseline

## Goal

Make the post-P4 product safer to run outside local development by moving deployment-sensitive values into configuration and adding production guardrails.

## Scope

- Add explicit app version and configurable CORS origins.
- Reject production startup when default local database credentials or wildcard origins are used.
- Return app version in the health response.
- Make Docker Compose ports and service credentials environment-driven.
- Update environment template and local runbook.

## Acceptance

- Local defaults continue to work without extra setup.
- Production mode requires non-default database credentials.
- Production mode requires explicit trusted origins.
- `GET /api/v1/health` returns status, service, environment, and version.
- Backend tests cover config parsing and production guardrails.

## Validation

```powershell
pytest backend\tests\test_config.py backend\tests\test_health.py
pytest backend\tests -q
```
