# Product Requirements Document

## Project Goal

Signal Tracker is an early-signal intelligence lifecycle tracking system. It helps users capture weak signals from information streams, preserve their history, and monitor whether they become verified opportunities, short-lived noise, or revived long-tail signals.

## Product Positioning

Signal Tracker is:

- A signal radar.
- An intelligence file manager.
- A lifecycle tracking system.
- An opportunity and risk judgment aid.

Signal Tracker is not:

- A general news portal.
- A social media dashboard.
- A pure RSS reader.
- A black-box investment recommendation engine.

## User Roles

| Role | Need |
| --- | --- |
| Operator | Add and monitor early signals without losing context |
| Analyst | Inspect evidence, timelines, entities, and state changes |
| Strategist | Track opportunity and credibility changes over time |
| Admin | Manage sources, workers, prompts, and system health |

## Core Scenarios

1. User submits a URL or text snippet.
2. System extracts summary, entities, keywords, source, timestamp, and signal type.
3. System creates a new intel file or attaches the evidence to an existing file.
4. System generates tracking keywords and entity queries.
5. System periodically checks for new related evidence.
6. System updates lifecycle status based on new evidence, inactivity, and score changes.
7. System alerts the user when a dormant file resurrects or when credibility/opportunity changes materially.
8. User opens an intel file to inspect first appearance, evidence timeline, status history, heat curve, and judgment.
9. System produces a daily briefing with new signals, meaningful updates, resurrected files, and likely noise.

## Functional Modules

| Module | Description | MVP |
| --- | --- | --- |
| Source Management | Manage source metadata, trust tier, source type, and fetch interval | Yes |
| Signal Inbox | Manual link/text intake and pending review | Yes |
| Extraction | AI structured extraction from raw items | Yes |
| Intel Files | Durable case files for tracked signals | Yes |
| Evidence Timeline | Attach raw items and analysis results to intel files | Yes |
| Lifecycle Engine | State transitions and lifecycle snapshots | Yes |
| Scoring Engine | Heat, credibility, opportunity, and risk scores | Yes |
| Tracking Jobs | Periodic keyword/entity follow-up searches | Limited |
| Alerts | Lifecycle and score-change alerts | Yes |
| Briefings | Daily digest of important changes | Yes |
| Archive & Trends | Daily snapshots for later trend analysis | Basic |
| Review Tools | Manual merge, split, status override, and note-taking | Later |

## MVP Scope

The MVP must prove the core lifecycle loop:

```text
Manual input
  -> AI extraction
  -> intel file creation
  -> evidence timeline
  -> lifecycle state update
  -> daily briefing
  -> resurrection alert
```

### MVP Screens

| Screen | Purpose |
| --- | --- |
| Inbox | Review newly submitted raw signals |
| Intel Files | Browse tracked signal cases |
| Intel File Detail | Timeline, scores, entities, status history |
| Alerts | Resurrection and major-change events |
| Briefing | Daily summary of meaningful changes |
| Sources | Manage source trust and metadata |

## Non-Functional Requirements

- Explainability: scores and lifecycle transitions must show their evidence.
- Auditability: first seen time and source must never be overwritten.
- Conservative merging: avoid attaching unrelated evidence automatically.
- Portability: local development must run with common services.
- Reliability: scheduled jobs should be idempotent and observable.
- Privacy: user notes and private sources must be separated from public evidence.
- Maintainability: every API/schema change must update docs and tests.

## Out Of Scope For First Build

- Large-scale social scraping.
- Paid source integrations.
- Multi-tenant billing.
- Advanced graph visualization.
- Fully autonomous opportunity investment decisions.
- Browser extension.
- Mobile native app.

## Acceptance Criteria

- User can submit one URL/text item and get a structured signal analysis.
- User can create an intel file from that signal.
- User can attach later evidence to the same file.
- System records first seen, last seen, and status history.
- System can mark a file as dormant after inactivity.
- System can mark a dormant file as resurrected when new evidence appears.
- Daily briefing lists new files, updated files, resurrected files, and likely noise.

## Open Product Questions

- Should the first version optimize for personal use or small-team use?
- What exact sources should be Tier 0 for AI/technology tracking?
- Should manual review be required before evidence attaches to an existing file?
- How aggressive should the first similarity merge rules be?
- Which notification channel is first: in-app only, email, Feishu, Telegram, or webhook?
