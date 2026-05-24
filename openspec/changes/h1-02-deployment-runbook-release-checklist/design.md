# Design

## Runbook

`docs/runbooks/deployment.md` describes the minimum production-like deployment path:

- required services
- environment contract
- preflight checks
- migration steps
- smoke tests
- rollback sequence

## Checklist

`docs/runbooks/release-checklist.md` is the operator-facing release gate. It keeps scope, configuration, database, validation, operations, and rollback checks in one place.

## Validation Script

`scripts/validate-release.ps1` is intentionally local and conservative. It verifies:

- Compose configuration renders
- backend tests pass
- frontend type-check passes
- frontend production build passes

It does not deploy infrastructure or mutate databases.
