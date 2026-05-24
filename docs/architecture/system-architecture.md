# System Architecture

## System Purpose

Signal Tracker turns scattered raw information into durable intelligence files and tracks their lifecycle over time.

## Proposed Stack

This planning scaffold does not mandate implementation, but the recommended default is:

| Layer | Recommended technology |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend API | FastAPI, Pydantic |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Queue | Celery or equivalent worker queue |
| Cache / Broker | Redis |
| AI | OpenAI-compatible structured output provider with mock fallback |
| Search | PostgreSQL full-text in MVP; optional vector search later |
| Tests | Pytest, TypeScript type-check, focused UI smoke tests |

## Core Domain Flow

```text
Source
  -> RawItem
  -> SignalAnalysis
  -> Evidence
  -> IntelFile
  -> IntelEvent
  -> LifecycleSnapshot
  -> AlertEvent / BriefingItem
```

## Modules

| Module | Responsibility |
| --- | --- |
| Sources | Source metadata, source type, trust tier, fetch policy |
| Intake | Manual URL/text submission and raw item normalization |
| Ingest | Scheduled fetchers for RSS/API/GitHub/job pages in later phases |
| Extraction | AI structured analysis of raw items |
| Matching | Decide whether a raw item creates a new intel file or attaches to an existing one |
| Intel Files | Main business object and evidence timeline |
| Lifecycle | State machine, transition rules, inactivity handling |
| Scoring | Heat, credibility, opportunity, risk, novelty |
| Tracking | Follow-up query generation and periodic monitoring |
| Alerts | Resurrection and major-score-change notifications |
| Briefings | Daily and weekly summaries |
| Archives | Daily snapshots for trends and auditability |
| Admin/Ops | Source health, worker logs, prompt versions, system metrics |

## Data Flow

### Manual MVP Flow

```text
User submits URL/text
  -> RawItem stored
  -> AI extraction returns structured SignalAnalysis
  -> Matching suggests new or existing IntelFile
  -> Evidence attached
  -> Lifecycle engine evaluates state
  -> Scoring engine updates scores
  -> Alert engine emits events if thresholds are crossed
  -> Briefing engine includes meaningful changes
```

### Scheduled Tracking Flow

```text
Active IntelFile
  -> Tracking queries generated from entities/keywords
  -> Worker searches configured sources
  -> New RawItems stored
  -> Evidence matching
  -> Lifecycle and scoring update
  -> Alerts and briefings
```

## API Areas

| Area | Example endpoints |
| --- | --- |
| Health | `GET /api/v1/health` |
| Sources | `GET/POST/PATCH /api/v1/sources` |
| Inbox | `POST /api/v1/inbox/submit`, `GET /api/v1/inbox` |
| Intel Files | `GET/POST/PATCH /api/v1/intel-files`, `GET /api/v1/intel-files/{id}` |
| Evidence | `POST /api/v1/intel-files/{id}/evidence`, `GET /api/v1/intel-files/{id}/timeline` |
| Lifecycle | `POST /api/v1/intel-files/{id}/evaluate`, `GET /api/v1/intel-files/{id}/lifecycle` |
| Alerts | `GET /api/v1/alerts`, `PATCH /api/v1/alerts/{id}` |
| Briefings | `GET /api/v1/briefings/daily` |
| Archives | `GET /api/v1/archives`, `GET /api/v1/trends` |

## Deployment Shape

```text
frontend
backend-api
worker
beat/scheduler
postgres
redis
```

## Architectural Rules

- `IntelFile` is the primary product object.
- `RawItem` and `Evidence` are supporting records, not the main UI destination.
- First-seen metadata is immutable after creation.
- Lifecycle transitions must be explainable and logged.
- Scoring v1 must be formula-based and inspectable.
- AI output must be stored with prompt version and model name.
- Scheduled jobs must be idempotent.

## Phase Architecture

| Phase | Architecture focus |
| --- | --- |
| P0 Planning | Docs, domain model, ADR, task board |
| P1 MVP | Manual intake, extraction, intel files, lifecycle, briefing |
| P2 Tracking | Scheduled searches, source connectors, resurrection alerts |
| P3 Intelligence | Better matching, scoring, trend archives, review tools |
| P4 Commercial | Auth, team workflow, channels, billing, deployment hardening |
