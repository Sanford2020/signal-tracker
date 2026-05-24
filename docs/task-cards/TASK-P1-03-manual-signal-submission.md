# TASK-P1-03: Manual Signal Submission

## Owner Skill

Backend + Frontend

## Goal

Allow a user to submit a URL or text snippet and create a `RawItem` in the inbox.

## Dependencies

- `TASK-P1-02`

## Read

- `docs/prd.md`
- `docs/specs/api-contracts.md`
- `docs/specs/ui-spec.md`

## Owned Files

- Backend inbox routes/services/schemas.
- Frontend inbox page and submission form.
- API client types.
- Tests for submission.

## Avoid

- Do not implement full extraction in this task.
- Do not implement auto crawling.
- Do not attach evidence to intel files yet.

## Acceptance Criteria

- User can submit `url`, `title`, and/or `content`.
- Backend stores a `RawItem`.
- If no source is provided, use a `manual` source.
- Duplicate content hash is handled gracefully.
- Frontend shows submitted item in Inbox.
- Error messages are readable.

## Validation

```powershell
cd backend
python -m pytest tests/test_inbox.py -q
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
