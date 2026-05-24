# TASK-H1-04: Staging Readiness Review

## Goal

Review the post-P4 and H1 hardening state, decide whether the product is ready for staging, and produce the remaining gap list.

## Scope

- Review H1-01 through H1-03 outputs.
- Confirm the release validation suite passes.
- Record staging readiness verdict.
- Identify next tasks for real hosted staging.

## Acceptance

- Staging readiness review document exists.
- `REVIEW.md` includes H1 approvals.
- `NEXT_TASK.md` points to the next executable task.
- Remaining risks are explicit and prioritized.

## Validation

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```
