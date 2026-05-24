# TASK-P1-11: MVP Acceptance Tests

## Owner Skill

Test + Review

## Goal

Verify the end-to-end MVP lifecycle loop.

## Dependencies

- `TASK-P1-10`

## Read

- `docs/prd.md`
- `docs/methodology/lifecycle-methodology.md`
- All P1 task cards.

## Owned Files

- Acceptance tests.
- Smoke scripts.
- `REVIEW.md`.

## Avoid

- Do not implement product features unless a tiny test hook is required and approved.

## Acceptance Scenario

1. Submit a raw signal.
2. Run extraction.
3. Create an intel file.
4. Attach first evidence.
5. Score file.
6. Mark file dormant through test fixture or time override.
7. Attach meaningful new evidence.
8. Lifecycle changes to `resurrected`.
9. Alert is created.
10. Daily briefing includes the resurrected file.

## Acceptance Criteria

- End-to-end test passes.
- Backend unit/integration tests pass.
- Frontend type-check/build pass.
- Review lists remaining risks.
- P1 verdict is `APPROVE`, `REQUEST_CHANGES`, or `BLOCK`.

## Validation

```powershell
cd backend
python -m pytest tests/ -q
cd ..\apps\web
npm run type-check
npm run build
```

## Output

```text
Changed:
Verified:
Risks:
Verdict:
Next:
```
