# TASKS.md

Task board for Signal Tracker.

## BACKLOG

- Browser extension for one-click capture.
- Hosted staging target and deployment adapter.
- Managed secrets, database, and Redis provisioning.
- Production auth hardening.
- Hosted backup automation and monitoring.
- Team comments and assignment.
- Vector search and entity graph.
- Paid source integrations.
- Multi-tenant accounts and billing.
- Export to Notion / Markdown / CSV.
- Weekly and monthly signal retrospectives.

## TODO

### P0 Planning Scaffold

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-20260522-P0-01: Project brief and PRD | Product | DONE | Brief and PRD define MVP and out-of-scope |
| TASK-20260522-P0-02: Lifecycle and scoring methodology | Product + Architecture | DONE | Lifecycle states and score formulas defined |
| TASK-20260522-P0-03: Architecture and data model | Architecture | DONE | Core entities and module flow defined |
| TASK-20260522-P0-04: AI development OS | Architecture + Documentation | DONE | AGENTS, SKILLS, TASKS, DECISIONS exist |
| TASK-20260522-P0-05: Commercial PRD | Product | DONE | Commercial tiers, roadmap, and sellable version defined |
| TASK-20260523-P0-06: AI employee execution package | Architecture + Documentation | DONE | Execution plan, task cards, specs, prompts, and handoff exist |
| TASK-20260523-P0-R: Planning review | Review | DONE | Verdict: APPROVE_WITH_FOLLOWUPS |

### P1 MVP Foundation

| Task | Skill | Status | Dependencies | Acceptance |
| --- | --- | --- | --- | --- |
| TASK-P1-02: Core database models | Backend | DONE | TASK-P1-01 | Sources, raw items, analyses, intel files, evidence, events, snapshots, alerts |
| TASK-P1-03: Manual signal submission | Backend + Frontend | DONE | TASK-P1-02 | User can submit URL/text and see inbox item |
| TASK-P1-04: AI extraction prompt and mock fallback | Backend | DONE | TASK-P1-03 | Structured extraction works with mock and live AI mode |
| TASK-P1-05: Intel file creation | Backend + Frontend | DONE | TASK-P1-04 | User can create file from signal and inspect detail |
| TASK-P1-06: Evidence timeline | Backend + Frontend | DONE | TASK-P1-05 | Evidence attaches to file and timeline renders |
| TASK-P1-07: Lifecycle evaluation v1 | Backend | DONE | TASK-P1-06 | State changes are logged with reasons |
| TASK-P1-08: Scoring engine v1 | Backend | DONE | TASK-P1-06 | Scores and explanations are stored |
| TASK-P1-09: Alerts v1 | Backend + Frontend | DONE | TASK-P1-07 | Resurrection and score threshold alerts show in UI |
| TASK-P1-10: Daily briefing v1 | Backend + Frontend | DONE | TASK-P1-08 | New, updated, resurrected, and opportunity files listed |
| TASK-P1-11: MVP acceptance tests | Test | DONE | TASK-P1-10 | Core lifecycle loop is tested |

### P2 Tracking

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-P2-01: Tracking query generation | Backend | DONE | Intel files generate follow-up queries |
| TASK-P2-02: Scheduled source checks | Backend | DONE | Worker fetches limited configured sources |
| TASK-P2-03: Conservative match suggestions | Backend + Frontend | DONE | System suggests evidence attachments with confidence |
| TASK-P2-04: Dormancy and resurrection worker | Backend | DONE | Dormant files revive when meaningful evidence appears |

### P3 Intelligence Workbench

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-P3-01: Accept match suggestions into evidence | Backend + Frontend | DONE | Accepted suggestions create RawItem evidence and close the suggestion |
| TASK-P3-02: Source provider framework | Backend | DONE | Configured providers can return source check results through the checker interface |
| TASK-P3-03: Status override with reason | Backend + Frontend | DONE | Analyst can override lifecycle status with logged rationale |
| TASK-P3-04: Trend archive snapshots | Backend | DONE | Daily snapshots preserve score/status history for trend review |
| TASK-P3-05: Weekly retrospective briefing | Backend + Frontend | DONE | Weekly report summarizes changed, revived, verified, and ignored signals |

### P4 Commercialization

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-P4-01: Auth and workspace foundation | Backend + Frontend | DONE | Users can sign in and access workspace-scoped data |
| TASK-P4-02: Team notes and ownership | Backend + Frontend | DONE | Files can have owner, comments, and review metadata |
| TASK-P4-03: Notification delivery layer | Backend | DONE | Alerts can be delivered through configured channels |
| TASK-P4-04: Report export | Backend + Frontend | DONE | Daily/weekly reports export to Markdown/PDF |
| TASK-P4-05: Usage limits and cost controls | Backend | DONE | Plan limits and AI/source check usage are tracked |

### H1 Product Hardening

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-H1-01: Production config and security baseline | Backend + Ops | DONE | Production config has explicit env contract and startup guardrails |
| TASK-H1-02: Deployment runbook and release checklist | Ops + Documentation | DONE | Staging release path, rollback checklist, and validation script exist |
| TASK-H1-03: Observability and backup baseline | Backend + Ops | DONE | Request tracing, basic logs, and backup/restore runbook exist |
| TASK-H1-04: Staging readiness review | Review + Ops | DONE | Readiness verdict and remaining staging gaps are documented |

### H2 Hosted Staging

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-H2-01: Hosted staging target and deployment adapter | Ops + Architecture | DONE | Hosted staging path is selected and documented |
| TASK-H2-02: Staging auth guard | Backend + Security | DONE | Public staging bootstrap/admin operations require an explicit staging secret |
| TASK-H2-03: Hosted staging smoke test script | Ops + Test | DONE | Remote staging health and frontend checks can be run from one command |
| TASK-H2-04: Hosted staging readiness review | Review + Ops | DONE | Render deploy readiness and owner-required actions are documented |

### H3 Access Control

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-H3-01: Workspace membership guard | Backend + Security | DONE | Production workspace routes require workspace membership |
| TASK-H3-02: Workspace member management | Backend + Frontend | DONE | Workspace admins can list and add members for staging collaboration |
| TASK-H3-03: Staging user access token | Backend + Frontend | DONE | Production workspace access requires user email plus user token |
| TASK-H3-04: Access control readiness review | Review + Security | DONE | H3 access-control posture and remaining auth gaps are documented |

### H4 Operations

| Task | Skill | Status | Acceptance |
| --- | --- | --- | --- |
| TASK-H4-01: Admin audit log | Backend + Frontend + Ops | DONE | Sensitive workspace/admin actions are recorded and visible to admins |
| TASK-H4-02: Audit log export | Backend + Frontend + Ops | DONE | Workspace admins can export audit events as CSV |
| TASK-H4-03: Security response headers | Backend + Security | DONE | API responses include baseline browser security headers |
| TASK-H4-04: Environment readiness check | Ops + Security | DONE | Deployment env files can be checked for required production/staging settings |
| TASK-H4-05: Admin rate limit | Backend + Security | DONE | Bootstrap/admin endpoints have configurable public staging rate limits |
| TASK-H4-06: Runtime readiness endpoint | Backend + Ops | DONE | API exposes database-backed readiness check for hosted staging |
| TASK-H4-07: Production env template | Ops + Security | DONE | Production-like env template exists and placeholder values fail readiness checks |
| TASK-H4-08: Predeploy checklist script | Ops + Test | DONE | One command runs local release validation and env readiness checks before hosted deploy |

## DOING

- None

## REVIEW

- None

## DONE

### P0 Planning Scaffold

- TASK-20260522-P0-01
- TASK-20260522-P0-02
- TASK-20260522-P0-03
- TASK-20260522-P0-04
- TASK-20260522-P0-05
- TASK-20260523-P0-06
- TASK-20260523-P0-R

### P1 MVP Foundation

- TASK-P1-01: Repo implementation scaffold
- TASK-P1-02: Core database models
- TASK-P1-03: Manual signal submission
- TASK-P1-04: AI extraction prompt and mock fallback
- TASK-P1-05: Intel file creation
- TASK-P1-06: Evidence timeline
- TASK-P1-07: Lifecycle evaluation v1
- TASK-P1-08: Scoring engine v1
- TASK-P1-09: Alerts v1
- TASK-P1-10: Daily briefing v1
- TASK-P1-11: MVP acceptance tests

### P2 Tracking

- TASK-P2-01: Tracking query generation
- TASK-P2-02: Scheduled source checks
- TASK-P2-03: Conservative match suggestions
- TASK-P2-04: Dormancy and resurrection worker

### P3 Intelligence Workbench

- TASK-P3-01: Accept match suggestions into evidence
- TASK-P3-02: Source provider framework
- TASK-P3-03: Status override with reason
- TASK-P3-04: Trend archive snapshots
- TASK-P3-05: Weekly retrospective briefing

### P4 Commercialization

- TASK-P4-01: Auth and workspace foundation
- TASK-P4-02: Team notes and ownership
- TASK-P4-03: Notification delivery layer
- TASK-P4-04: Report export
- TASK-P4-05: Usage limits and cost controls

### H1 Product Hardening

- TASK-H1-01: Production config and security baseline
- TASK-H1-02: Deployment runbook and release checklist
- TASK-H1-03: Observability and backup baseline
- TASK-H1-04: Staging readiness review

### H2 Hosted Staging

- TASK-H2-01: Hosted staging target and deployment adapter
- TASK-H2-02: Staging auth guard
- TASK-H2-03: Hosted staging smoke test script
- TASK-H2-04: Hosted staging readiness review

### H3 Access Control

- TASK-H3-01: Workspace membership guard
- TASK-H3-02: Workspace member management
- TASK-H3-03: Staging user access token
- TASK-H3-04: Access control readiness review

### H4 Operations

- TASK-H4-01: Admin audit log
- TASK-H4-02: Audit log export
- TASK-H4-03: Security response headers
- TASK-H4-04: Environment readiness check
- TASK-H4-05: Admin rate limit
- TASK-H4-06: Runtime readiness endpoint
- TASK-H4-07: Production env template
- TASK-H4-08: Predeploy checklist script

## BLOCKED

- None

## Task Template

```text
Task ID:
Goal:
Owner Skill:
Scope:
Avoid:
Acceptance Criteria:
Validation:
Notes:
```
