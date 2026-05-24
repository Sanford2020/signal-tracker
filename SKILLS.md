# SKILLS.md

Signal Tracker uses Skills as scoped work modes. A Skill is not an autonomous project owner. The Master Agent decides; Skills execute.

## Skill Lifecycle

```text
Master reads TASKS.md
  -> selects Skill
  -> provides scope, context, avoided files, validation
  -> Skill executes
  -> Skill returns changed files, validation result, risks
  -> Master reviews or routes to Review Skill
  -> TASKS / DECISIONS / docs are updated
```

## Skill Catalog

| Skill | Purpose | Typical files |
| --- | --- | --- |
| Product Skill | PRD, scope, user flows, acceptance criteria | `docs/prd.md`, `PROJECT_BRIEF.md`, `docs/plans/*` |
| Architecture Skill | Data model, module boundaries, API contracts, ADR | `docs/architecture/*`, `DECISIONS.md` |
| Backend Skill | API, database, workers, lifecycle/scoring services | `backend/**`, `workers/**`, migrations |
| Frontend Skill | UI, routes, client types, state | `apps/web/**` |
| Test Skill | Automated verification and smoke tests | `tests/**`, scripts |
| Review Skill | Findings, risks, verdicts | `REVIEW.md`, inline comments |
| Documentation Skill | API, deployment, handoff, operations docs | `docs/**`, `README.md` |
| Deployment Skill | Docker, env, release, monitoring | `docker/**`, scripts, deployment docs |

## Boundaries

- Product Skill should not implement backend or frontend code.
- Architecture Skill should not make large code changes.
- Backend Skill should not redesign UI.
- Frontend Skill should not change backend behavior unless task explicitly includes contract updates.
- Test Skill may create tests and small fixtures but should not change product behavior.
- Review Skill should report findings first and avoid unnecessary refactors.

## Task Input Format

Every Skill should receive:

```text
Task ID:
Goal:
Owned files:
Avoided files:
Relevant docs:
Acceptance criteria:
Validation command:
Notes:
```

## Task Output Format

Every Skill should return:

```text
Changed:
Verified:
Risks:
Open questions:
Next:
```

## Context Rules

- Load only relevant files.
- Summarize long logs.
- Do not paste full generated code into planning docs.
- If a task discovers architecture ambiguity, stop and request Master/ADR handling.
