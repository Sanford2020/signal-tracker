# TASK-P1-09: Alerts V1

## Owner Skill

Backend + Frontend

## Goal

Create and display alerts for meaningful lifecycle and score changes.

## Dependencies

- `TASK-P1-07`
- `TASK-P1-08`

## Read

- `docs/methodology/lifecycle-methodology.md`
- `docs/methodology/scoring-methodology.md`
- `docs/specs/ui-spec.md`

## Owned Files

- Alert service.
- Alert routes.
- Alerts page.
- Tests.

## Avoid

- Do not add external notification channels yet.
- Do not create alerts for every evidence attachment.

## Required Alert Types

- `resurrected`
- `heat_spike`
- `credibility_up`
- `risk_up`
- `opportunity_up`
- `verified`
- `debunked`

## Acceptance Criteria

- Alert event created for `dormant -> resurrected`.
- Alert event created when opportunity score crosses threshold.
- Alert list page shows severity, file, message, status, created time.
- User can acknowledge or dismiss alert.
- Tests avoid duplicate alerts for the same transition.

## Validation

```powershell
cd backend
python -m pytest tests/test_alerts.py -q
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
