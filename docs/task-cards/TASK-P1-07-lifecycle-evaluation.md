# TASK-P1-07: Lifecycle Evaluation V1

## Owner Skill

Backend

## Goal

Implement the v1 lifecycle state engine.

## Dependencies

- `TASK-P1-06`

## Read

- `docs/methodology/lifecycle-methodology.md`
- `docs/methodology/scoring-methodology.md`
- `DECISIONS.md`

## Owned Files

- Lifecycle service.
- Lifecycle tests.
- Snapshot/event creation logic.

## Avoid

- Do not make lifecycle state free-form.
- Do not call live AI from lifecycle tests.
- Do not hide transition rationale.

## Required States

- `new`
- `watching`
- `spreading`
- `validating`
- `cooling`
- `dormant`
- `resurrected`
- `verified`
- `debunked`
- `noise`
- `archived`

## Acceptance Criteria

- Engine evaluates an `IntelFile` and returns previous status, next status, reason, evidence IDs, and score changes.
- Creates `IntelEvent` for state changes.
- Creates `LifecycleSnapshot` for each evaluation.
- Dormancy threshold is configurable.
- Dormant file with meaningful new evidence becomes `resurrected`.
- Unit tests cover at least: new, spreading, dormant, resurrected, verified, debunked, noise.

## Validation

```powershell
cd backend
python -m pytest tests/test_lifecycle.py -q
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
