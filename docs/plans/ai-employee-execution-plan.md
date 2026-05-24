# AI Employee Execution Plan

## Purpose

This plan turns Signal Tracker from planning docs into AI-executable work.

The rule is simple:

```text
Master Agent owns decisions.
AI employees own scoped task cards.
Review gates decide whether work moves forward.
```

## Operating Model

| Role | AI employee | Responsibility |
| --- | --- | --- |
| Master | Master Agent | Prioritize tasks, protect scope, approve ADRs |
| Product | Product Skill | Clarify scenarios, acceptance criteria, copy |
| Architect | Architecture Skill | Domain model, API contracts, module boundaries |
| Backend | Backend Skill | FastAPI, DB models, services, workers |
| Frontend | Frontend Skill | UI routes, components, client integration |
| QA | Test Skill | Tests, smoke scripts, regression checks |
| Reviewer | Review Skill | Findings, risks, milestone verdicts |
| Docs/Ops | Documentation + Deployment Skills | Runbooks, env, Docker, deployment notes |

## OpenSpec Change Workflow

Implementation tasks use an OpenSpec-inspired change package:

```text
openspec/changes/<change-id>/
  proposal.md   why this change exists and what is in/out
  design.md     technical approach and boundaries
  tasks.md      implementation checklist
  specs/        optional delta specs
```

Current agreed behavior lives in:

```text
openspec/specs/
```

AI employees should treat `openspec/specs/` as behavior truth and `openspec/changes/*` as the active construction plan.

## Execution Phases

### P0: Planning Approval

Goal: Confirm docs are consistent enough to start implementation.

Active cards:

- `TASK-20260523-P0-R`

Exit gate:

- Review verdict is `APPROVE` or `APPROVE_WITH_FOLLOWUPS`.

### P1A: Implementation Scaffold

Goal: Create runnable repo skeleton.

Active cards:

- `TASK-P1-01`

Change package:

- `openspec/changes/p1-01-repo-scaffold/`

Exit gate:

- Backend health endpoint works.
- Frontend home page loads.
- Database migration command exists.
- Worker process can start.
- Test commands exist.

### P1B: Domain Foundation

Goal: Implement core database and backend domain model.

Active cards:

- `TASK-P1-02`
- `TASK-P1-04` can begin after model skeleton if AI/mock abstraction is ready.

Change package:

- `openspec/changes/p1-02-core-domain-model/`

Exit gate:

- Models and migrations exist.
- Unit tests cover create/read flows.
- Domain names match `data-model.md`.

### P1C: Manual Intake And Extraction

Goal: User can submit a signal and receive structured analysis.

Active cards:

- `TASK-P1-03`
- `TASK-P1-04`

Exit gate:

- Manual text/URL submission creates `RawItem`.
- Extraction creates `SignalAnalysis`.
- Mock mode works without external API key.

### P1D: Intel File Loop

Goal: User can create an intel file and attach evidence.

Active cards:

- `TASK-P1-05`
- `TASK-P1-06`

Exit gate:

- Intel file detail page shows metadata and evidence timeline.
- First-seen and last-seen are stored.
- Evidence attachment creates timeline event.

### P1E: Lifecycle, Scoring, Alerts

Goal: Prove the core product differentiation.

Active cards:

- `TASK-P1-07`
- `TASK-P1-08`
- `TASK-P1-09`

Exit gate:

- Dormant to resurrected transition is testable.
- Score snapshots include explanation.
- Alert event is created for resurrection and opportunity threshold.

### P1F: Briefing And Acceptance

Goal: Produce the daily operating output.

Active cards:

- `TASK-P1-10`
- `TASK-P1-11`

Exit gate:

- Daily briefing lists new, updated, resurrected, and opportunity files.
- End-to-end lifecycle smoke test passes.
- Review approves P1.

## Serial And Parallel Rules

### Strongly Serial

- `TASK-P1-01` before all implementation tasks.
- `TASK-P1-02` before user-facing file/evidence features.
- `TASK-P1-07` before lifecycle alerts.
- `TASK-P1-11` after P1 features exist.

### Can Parallelize

- Frontend static shell can start after `TASK-P1-01`.
- AI extraction prompt can start after `RawItem` and `SignalAnalysis` schema draft.
- Docs/Ops can update alongside implementation if contracts are stable.

### Do Not Parallelize

- Two AI employees editing the same file area.
- Backend API schema and frontend client without a contract note.
- Lifecycle and scoring logic unless interfaces are agreed.

## Milestone Review Gates

| Gate | Reviewer checks |
| --- | --- |
| P0 Review | Planning consistency, task readiness |
| P1A Review | Repo boots, commands work |
| P1B Review | Data model, migrations, naming |
| P1D Review | Intel file loop and timeline |
| P1E Review | Lifecycle and score explainability |
| P1F Review | End-to-end MVP |

## Owner Instructions

When assigning an AI employee, provide:

```text
Read AGENTS.md, SKILLS.md, your task card, and your openspec change package.
Do not read the entire repo unless blocked.
Stay inside Owned files.
Return Changed / Verified / Risks / Next.
```

## Definition Of Ready

A task is ready when it has:

- Clear goal.
- Owned files.
- Avoided files.
- Acceptance criteria.
- Validation command.
- Dependency status.

## Definition Of Done

A task is done when:

- Acceptance criteria are met.
- Tests or validation pass.
- Docs are updated where relevant.
- Reviewer gives `APPROVE`.
- `TASKS.md` is updated.
