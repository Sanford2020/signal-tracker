# TASK-P1-10: Daily Briefing V1

## Owner Skill

Backend + Frontend

## Goal

Generate a daily briefing that summarizes meaningful intel file changes.

## Dependencies

- `TASK-P1-08`
- `TASK-P1-09`

## Read

- `docs/prd.md`
- `docs/specs/briefing-spec.md`
- `docs/specs/ui-spec.md`

## Owned Files

- Briefing service.
- Briefing route.
- Briefing page.
- Briefing tests.

## Avoid

- Do not implement full report builder.
- Do not add email/Slack delivery yet.

## Briefing Sections

- New intel files.
- Updated intel files.
- Resurrected signals.
- High opportunity files.
- High risk/noise candidates.

## Acceptance Criteria

- API returns briefing for a configurable time window.
- Items include file ID, title, status, scores, reason, and key evidence.
- Frontend briefing page renders sections.
- Empty states are clear.
- Tests cover briefing selection logic.

## Validation

```powershell
cd backend
python -m pytest tests/test_briefings.py -q
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
