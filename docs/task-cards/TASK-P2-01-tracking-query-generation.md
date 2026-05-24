# TASK-P2-01: Tracking Query Generation

## Owner Skill

Backend

## Goal

Generate follow-up tracking queries for IntelFiles so later scheduled checks have a deterministic input list.

## Dependencies

- `TASK-P1-04`
- `TASK-P1-05`

## Read

- `docs/specs/ai-extraction-contract.md`
- `docs/methodology/source-taxonomy.md`
- `docs/architecture/data-model.md`

## Owned Files

- Tracking query model/migration.
- Tracking query service/API.
- Tests.

## Avoid

- Do not fetch external sources yet.
- Do not build crawler or scheduler.
- Do not use live AI for tests.

## Acceptance Criteria

- IntelFile can generate tracking queries from analysis suggestions, entities, keywords, title, and thesis.
- Queries are deduplicated and persisted.
- Regeneration is idempotent.
- Queries include source hints and enabled flag for later scheduled checks.
- API returns generated queries.

## Validation

```powershell
cd backend
python -m pytest tests/test_tracking_queries.py -q
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
