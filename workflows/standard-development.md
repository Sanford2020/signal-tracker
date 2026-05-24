# Standard Development Workflow

## 1. Select Task

Master selects one task from `TASKS.md`.

## 2. Confirm Change Package

For implementation work, Master confirms a matching folder exists under:

```text
openspec/changes/<change-id>/
```

If no change package exists, create one before coding.

## 3. Assign Skill

Master assigns:

- Owner Skill.
- Scope files.
- Avoided files.
- Relevant docs.
- Acceptance criteria.
- Validation command.

## 4. Execute

Skill implements only the assigned scope.

## 5. Validate

Skill runs task validation and verifies behavior against the relevant OpenSpec scenarios.
If validation cannot run, it records why.

## 6. Document

Update docs when behavior, API, data model, lifecycle, scoring, or deployment changes.

## 7. Review

Move task to REVIEW and run Review Skill.

## 8. Archive / Sync Specs

After approval, sync completed behavior into `openspec/specs/` if the change added or modified behavior.

## 9. Close

Move to DONE only after approval.

## Handoff Format

```text
Changed:
Verified:
Risks:
Next:
```
