# MVP Roadmap

## Principle

Build the smallest version that proves the intelligence lifecycle loop.

Do not build a large crawler or generic news dashboard first.

## Phase P0: Planning Scaffold

Goal: Make the project ready for AI-assisted development.

Deliverables:

- Project brief.
- PRD.
- Architecture.
- Data model.
- Lifecycle methodology.
- Scoring methodology.
- Source taxonomy.
- AI development OS.

Exit criteria:

- Review approves P0 docs.
- P1 tasks have clear acceptance criteria.

## Phase P1: Manual Lifecycle MVP

Goal: A user can submit a signal and track it as an intel file.

Features:

- Manual URL/text submission.
- Raw item storage.
- AI extraction with mock fallback.
- Intel file creation.
- Evidence attachment.
- Timeline view.
- Lifecycle evaluation.
- Score snapshots.
- Basic alerts.
- Daily briefing.

Exit criteria:

- End-to-end lifecycle test passes.
- A dormant file can become resurrected in a test fixture.
- UI shows file detail with evidence timeline and score explanations.

## Phase P2: Automated Tracking

Goal: System can watch existing files for follow-up evidence.

Features:

- Tracking query generation.
- Scheduled worker.
- Limited source connectors.
- Match suggestions.
- Dormancy and resurrection worker.

Exit criteria:

- Worker finds or ingests follow-up evidence.
- Match suggestions include confidence and rationale.
- Resurrection alert fires only for meaningful evidence.

## Phase P3: Intelligence Workbench

Goal: Improve judgment and review quality.

Features:

- Manual merge and split.
- Status override with reason.
- Better score trend charts.
- Entity and keyword drilldowns.
- Weekly retrospectives.
- Archive and trend analysis.

Exit criteria:

- Analyst can explain a signal's history from first seen to current state.
- Review controls reduce false merges and alert noise.

## Phase P4: Commercialization

Goal: Prepare for team and commercial usage.

Features:

- Auth and roles.
- Notification channels.
- Team notes.
- Source packs by niche.
- Deployment hardening.
- Billing and limits.

Exit criteria:

- A small team can run daily intelligence workflow reliably.
