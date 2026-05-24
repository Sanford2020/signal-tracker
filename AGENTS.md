# AGENTS.md

Signal Tracker uses a Single Master Agent plus Multiple Skills model.

The goal is to make AI-assisted development controlled, reviewable, and resistant to scope drift.

## Core Rule

Only one Master Agent owns product and architecture decisions. Skills execute scoped tasks.

```text
Human owner
  -> Master Agent
  -> Product / Architecture / Backend / Frontend / Test / Review / Docs Skills
  -> Verified task output
```

## AI Working Principles

1. Task before code: no business logic changes without a `TASKS.md` entry.
2. ADR before architecture change: major decisions go to `DECISIONS.md`.
3. Small tasks: every task must have clear scope and validation.
4. Minimal context: load only files required for the task.
5. No hidden scope expansion: blockers return to Master as notes or new tasks.
6. Tests define done: task is not done until validation passes or is explicitly blocked.
7. Docs follow changes: API, data model, lifecycle, and scoring changes must update docs.
8. Review before done: Review Skill must approve meaningful product or architecture changes.

## Tool Role Mapping

| Role | Responsibility |
| --- | --- |
| Master Agent | Planning, task breakdown, architecture decisions, review routing |
| Product Skill | PRD, user stories, acceptance criteria, MVP boundaries |
| Architecture Skill | module boundaries, data model, API contracts, ADRs |
| Backend Skill | API, database, workers, lifecycle/scoring engines |
| Frontend Skill | UI, API client, interaction flows |
| Test Skill | unit tests, integration tests, smoke checks |
| Review Skill | code review, architecture review, risk review |
| Documentation Skill | docs, runbooks, API reference, handoff notes |
| Deployment Skill | Docker, env, migrations, release workflows |

## Before Editing Code

1. Confirm the task exists in `TASKS.md`.
2. Read only relevant planning docs.
3. Identify owned files and avoided files.
4. Confirm acceptance criteria and validation command.
5. Check whether the change requires an ADR.

## After Editing Code

1. Run validation.
2. Update docs if contracts or behavior changed.
3. Add a short task note.
4. Move task to REVIEW.
5. Do not mark DONE without Review approval.

## Review Rules

Review output should use:

- `P0`: must fix before merge.
- `P1`: should fix soon; may block depending on risk.
- `P2`: improvement or follow-up.

Verdict:

- `APPROVE`
- `REQUEST_CHANGES`
- `BLOCK`

## Forbidden

- Starting implementation before planning docs are accepted.
- Replacing `IntelFile` with a generic article/news model.
- Adding major infrastructure before MVP proves lifecycle loop.
- Making scoring black-box without explanation.
- Auto-merging evidence with low confidence.
- Changing API without updating docs and types.
- Hiding failed tests.
- Committing secrets.

## Definition Of Done

- Task acceptance criteria met.
- Validation command passes or blocker is documented.
- Relevant docs updated.
- Review verdict is `APPROVE`.
- `TASKS.md` status updated.
