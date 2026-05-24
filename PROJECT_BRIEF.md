# Signal Tracker Project Brief

## 1. Project Overview

- Project name: Signal Tracker
- Project code: signal-tracker
- Current phase: Planning scaffold
- Owner: Sanford
- Created: 2026-05-22
- Primary goal: Prepare an AI-developable project plan before implementation.

## 2. One-Line Goal

Signal Tracker captures early abnormal information signals, creates intelligence files for them, and tracks their lifecycle until they disappear, revive, get verified, get debunked, or turn into opportunities.

## 3. Background And Motivation

Most information systems optimize for current heat. Signal Tracker optimizes for signal continuity:

- A weak signal appears once and becomes hot briefly.
- The signal is forgotten because no one tracks follow-up evidence.
- Weeks later, related evidence appears again, but the original context is lost.
- Valuable opportunities are missed because the lifecycle was not preserved.

Signal Tracker exists to preserve that context.

## 4. Target Users

| User type | Core need | Use case | Success standard |
| --- | --- | --- | --- |
| Founder / operator | Find early opportunities | Track AI tools, product shifts, hiring signals, policy changes | Receives actionable follow-up alerts before mainstream coverage |
| Investor / strategist | Monitor weak signals | Track companies, sectors, regulation, funding rumors | Can see evidence history and credibility changes |
| Analyst / researcher | Maintain intelligence files | Connect scattered posts, news, GitHub updates, job posts | Can explain signal history from first appearance to current state |
| Content operator | Build topic pipeline | Follow topics from rumor to trend | Can produce timely content from revived or verified signals |

## 5. Scope

### Must Include In MVP

- Manual signal submission by URL or text.
- Source and raw item storage.
- AI structured extraction: summary, entities, keywords, signal type.
- Intel file creation and evidence attachment.
- Basic duplicate/similarity merge rules.
- Lifecycle status: new, spreading, cooling, dormant, resurrected, verified, debunked, noise.
- Daily briefing: new signals, new evidence, resurrected files, high-opportunity files.
- Basic alert events for resurrection and score threshold changes.

### Out Of Scope For MVP

- Fully automated social crawling at scale.
- Complex entity graph UI.
- Vector database dependency unless proven necessary.
- Team permissions and billing.
- Mobile app.
- Trading or financial advice automation.

## 6. First Commercial Niche

Start with AI / technology opportunity tracking:

- AI products and model launches.
- Open-source project activity.
- GitHub releases and commits.
- Hiring and career page changes.
- Founder or employee posts.
- Funding and acquisition rumors.
- Policy and platform-rule changes.

This niche has fast-moving signals, public evidence, and clear user pain around missed context.

## 7. Core Deliverables

| Deliverable | Description | Verification |
| --- | --- | --- |
| Planning scaffold | PRD, architecture, lifecycle, scoring, source taxonomy | Docs complete and internally consistent |
| AI development OS | AGENTS, SKILLS, TASKS, DECISIONS | Every task has scope and acceptance criteria |
| MVP architecture | Domain model and API shape | Implementation tasks can be created without ambiguity |
| Lifecycle methodology | State machine and transitions | Testable rules exist for status changes |
| Scoring methodology | v1 explainable scoring | Formula inputs and outputs are defined |

## 8. Success Criteria For Planning Phase

- AI can implement the project from `TASKS.md` without inventing product scope.
- Domain objects are clear: `Signal`, `Evidence`, `IntelFile`, `IntelEvent`, `LifecycleSnapshot`, `AlertEvent`.
- Major decisions are captured in `DECISIONS.md`.
- MVP can be built as small tasks with validation commands.

## 9. Key Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Product becomes a generic news reader | Loses differentiation | Keep `IntelFile` as the primary object, not `Article` |
| AI agents overbuild crawling | Scope explosion | Start with manual input and limited sources |
| Scoring becomes black box | Users cannot trust output | Use explainable v1 formulas |
| Similarity merge is unreliable | Wrong evidence attached | Use conservative merge rules and manual override |
| Alerts become noisy | User ignores system | Alert only on lifecycle transitions and major score changes |

## 10. Guiding Principle

Every feature must answer one of these questions:

```text
What was first seen?
What changed?
What evidence supports it?
What is its current lifecycle state?
Is it becoming an opportunity or noise?
```
