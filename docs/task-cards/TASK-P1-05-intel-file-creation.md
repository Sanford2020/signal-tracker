# TASK-P1-05: Intel File Creation

## Owner Skill

Backend + Frontend

## Goal

Create an `IntelFile` from an analyzed signal.

## Dependencies

- `TASK-P1-04`

## Read

- `docs/architecture/data-model.md`
- `docs/methodology/lifecycle-methodology.md`
- `docs/specs/api-contracts.md`
- `docs/specs/ui-spec.md`

## Owned Files

- Backend intel file routes/services.
- Frontend intel file list and detail skeleton.
- Tests for file creation.

## Avoid

- Do not implement aggressive matching.
- Do not implement team collaboration.
- Do not implement graph UI.

## Acceptance Criteria

- User can create an `IntelFile` from `SignalAnalysis`.
- `IntelFile` starts with status `new` or `watching` according to lifecycle rules.
- First evidence is attached as `first_seen`.
- `first_seen_at` and `last_seen_at` are set.
- An `IntelEvent` is created.
- File appears in Intel Files list.
- Detail page shows title, thesis, status, entities, keywords, and scores.

## Validation

```powershell
cd backend
python -m pytest tests/test_intel_files.py -q
cd ..\apps\web
npm run type-check
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
