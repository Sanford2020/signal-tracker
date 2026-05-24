# TASK-P1-06: Evidence Timeline

## Owner Skill

Backend + Frontend

## Goal

Allow evidence to be attached to an intel file and shown as a timeline.

## Dependencies

- `TASK-P1-05`

## Read

- `docs/architecture/data-model.md`
- `docs/methodology/lifecycle-methodology.md`
- `docs/specs/ui-spec.md`

## Owned Files

- Evidence routes/services.
- Timeline API.
- Intel file detail timeline UI.
- Evidence tests.

## Avoid

- Do not implement automated matching yet.
- Do not rewrite file creation flow.

## Acceptance Criteria

- User/system can attach a `RawItem` to an `IntelFile`.
- Evidence has type, confidence, attached_by, and rationale.
- Timeline shows file creation, evidence added, and status events.
- `last_seen_at`, `source_count`, and `evidence_count` update.
- Duplicate evidence attachment is prevented.

## Validation

```powershell
cd backend
python -m pytest tests/test_evidence_timeline.py -q
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
