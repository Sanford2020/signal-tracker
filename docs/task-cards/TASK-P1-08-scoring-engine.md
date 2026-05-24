# TASK-P1-08: Scoring Engine V1

## Owner Skill

Backend

## Goal

Implement explainable v1 scoring for intel files.

## Dependencies

- `TASK-P1-06`

## Read

- `docs/methodology/scoring-methodology.md`

## Owned Files

- Scoring service.
- Score snapshot logic.
- Scoring tests.

## Avoid

- Do not replace formulas with black-box AI.
- Do not update lifecycle state directly unless through lifecycle service.

## Required Scores

- novelty_score
- heat_score
- credibility_score
- opportunity_score
- risk_score

## Acceptance Criteria

- Scoring service calculates all v1 scores.
- Each score update stores rationale.
- Inputs are inspectable in test output or stored metadata.
- Scores are clamped to 0-10.
- Opportunity alert threshold can read `opportunity_score`.
- Tests cover normal, high-risk, high-opportunity, and low-credibility cases.

## Validation

```powershell
cd backend
python -m pytest tests/test_scoring.py -q
```

## Output

```text
Changed:
Verified:
Risks:
Next:
```
