# TASK-P1-02: Core Database Models

## Owner Skill

Backend

## Goal

Implement the core domain database models and migrations.

## Dependencies

- `TASK-P1-01`

## Read

- `docs/architecture/data-model.md`
- `docs/methodology/lifecycle-methodology.md`
- `docs/methodology/scoring-methodology.md`
- `DECISIONS.md`

## Owned Files

- Backend models.
- Backend schemas.
- Database migrations.
- Backend tests for model creation and relationships.

## Avoid

- Do not implement UI.
- Do not implement full lifecycle engine yet.
- Do not add vector database.

## Required Models

- `Source`
- `RawItem`
- `SignalAnalysis`
- `IntelFile`
- `Evidence`
- `IntelEvent`
- `LifecycleSnapshot`
- `AlertEvent`

## Acceptance Criteria

- Models match names and core fields in `data-model.md`.
- Migrations create all MVP tables.
- Relationships work:
  - Source to RawItem.
  - RawItem to SignalAnalysis.
  - IntelFile to Evidence.
  - IntelFile to IntelEvent.
  - IntelFile to LifecycleSnapshot.
  - IntelFile to AlertEvent.
- `RawItem` supports content hash dedupe.
- `IntelFile.first_seen_at` and `last_seen_at` are represented.
- Tests create a full sample chain.

## Validation

```powershell
cd backend
python -m pytest tests/test_models.py -q
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
