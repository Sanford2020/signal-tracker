# Data Model

## Core Entities

### Source

Represents where raw information came from.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `name` | Human-readable source name |
| `source_type` | rss, x, reddit, github, careers, news, search, manual, other |
| `url` | Source URL when applicable |
| `category` | Source taxonomy category |
| `trust_tier` | 0, 1, 2, 3 |
| `fetch_interval_minutes` | Suggested worker frequency |
| `enabled` | Whether scheduled ingest is active |
| `license_notes` | Compliance notes |

### RawItem

Immutable captured information unit.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `source_id` | Source reference |
| `title` | Raw item title |
| `url` | Canonical URL |
| `content` | Extracted text or submitted text; nullable for URL-only intake pending fetch |
| `content_hash` | Deduplication hash |
| `published_at` | Source publication time |
| `captured_at` | System capture time |
| `raw_json` | Original parser payload |

### SignalAnalysis

AI or rule-based structured analysis for a raw item.

| Field | Purpose |
| --- | --- |
| `raw_item_id` | Raw item reference |
| `summary` | Factual summary |
| `signal_type` | hiring, product, policy, funding, github, rumor, research, market, other |
| `entities` | People, organizations, products, countries, projects |
| `keywords` | Tracking keywords |
| `claims` | Main claims extracted from the item |
| `suggested_tracking_queries` | Follow-up search queries from extraction |
| `novelty_score` | How early or unusual this appears |
| `relevance_score` | Business/topic relevance |
| `credibility_hint` | Initial source/evidence credibility |
| `risk_hint` | Initial risk assessment hint |
| `opportunity_types` | Opportunity categories from extraction |
| `rationale` | Extraction judgment explanation |
| `language` | Detected language |
| `model` | AI model used |
| `prompt_version` | Prompt version |
| `raw_output` | Stored AI response |

### IntelFile

The primary durable intelligence object.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `title` | Case title |
| `thesis` | Short statement of what the signal may mean |
| `status` | Current lifecycle state |
| `first_seen_at` | Earliest evidence time |
| `last_seen_at` | Most recent evidence time |
| `primary_signal_type` | Main signal type |
| `entities` | Canonical entities |
| `keywords` | Tracking keywords |
| `source_count` | Number of distinct sources |
| `evidence_count` | Number of attached evidence items |
| `heat_score` | Current heat |
| `credibility_score` | Current credibility |
| `opportunity_score` | Current opportunity score |
| `risk_score` | Current risk score |
| `owner_notes` | User notes |

### Evidence

Links a raw item to an intel file and describes its role.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `intel_file_id` | Intel file reference |
| `raw_item_id` | Raw item reference |
| `evidence_type` | first_seen, follow_up, corroboration, contradiction, correction, noise |
| `confidence` | Matching confidence |
| `attached_by` | system, user, admin |
| `rationale` | Why this evidence belongs to the file |

### IntelEvent

A timeline event derived from evidence or manual updates.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `intel_file_id` | Intel file reference |
| `event_type` | created, evidence_added, status_changed, score_changed, note_added |
| `event_time` | Event time |
| `title` | Short event title |
| `description` | Human-readable explanation |
| `source_evidence_id` | Optional evidence reference |
| `metadata` | Structured event payload |

### LifecycleSnapshot

Point-in-time state and score record.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `intel_file_id` | Intel file reference |
| `snapshot_time` | Snapshot timestamp |
| `status` | Lifecycle state |
| `heat_score` | Heat at this time |
| `credibility_score` | Credibility at this time |
| `opportunity_score` | Opportunity at this time |
| `risk_score` | Risk at this time |
| `reason` | Transition or scoring explanation |

### AlertEvent

Notification-worthy lifecycle or score event.

| Field | Purpose |
| --- | --- |
| `id` | Primary key |
| `intel_file_id` | Intel file reference |
| `alert_type` | resurrected, heat_spike, credibility_up, risk_up, opportunity_up |
| `severity` | info, watch, important, urgent |
| `message` | Human-readable alert |
| `status` | pending, sent, acknowledged, dismissed |
| `channel` | in_app, email, webhook, feishu, telegram |
| `created_at` | Creation time |

## Relationship Diagram

```text
Source 1--N RawItem
RawItem 1--1 SignalAnalysis
IntelFile 1--N Evidence
RawItem 1--N Evidence
IntelFile 1--N IntelEvent
IntelFile 1--N LifecycleSnapshot
IntelFile 1--N AlertEvent
```

## Design Decisions

- Keep `RawItem` immutable for auditability.
- Keep `IntelFile.first_seen_at` immutable except when earlier evidence is manually attached.
- Store AI outputs for traceability.
- Separate `Evidence` from `RawItem` so one raw item can support multiple intel files if needed.
- Store lifecycle snapshots instead of only current status.

## MVP Tables

The first implementation should prioritize:

```text
sources
raw_items
signal_analyses
intel_files
evidence
intel_events
lifecycle_snapshots
alert_events
```
