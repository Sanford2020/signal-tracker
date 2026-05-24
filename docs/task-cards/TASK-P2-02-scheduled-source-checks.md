# TASK-P2-02: Scheduled Source Checks

## Owner Skill

Backend

## Goal

Run limited source checks from enabled tracking queries and record attempts/results for later matching.

## Dependencies

- `TASK-P2-01`

## Read

- `docs/methodology/source-taxonomy.md`
- `docs/task-cards/TASK-P2-01-tracking-query-generation.md`

## Owned Files

- Source check run/result models.
- Source check runner service.
- Source check API/tests.

## Avoid

- Do not implement broad crawling.
- Do not call external networks in tests.
- Do not auto-attach evidence to files.

## Acceptance Criteria

- Runner consumes enabled tracking queries only.
- Runner has a configurable per-run limit.
- Each run records status, checked query count, result count, and errors.
- Results are stored for later matching.
- Tests use a mock checker.

## Validation

```powershell
cd backend
python -m pytest tests/test_source_checks.py -q
```
