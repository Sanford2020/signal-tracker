# API Contracts

## Purpose

This document gives backend and frontend AI employees a shared API target for the MVP.

Contracts may evolve, but changes must update this file and frontend types in the same task.

## Response Envelope

Use a consistent envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

Error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "not_found",
    "message": "Intel file not found"
  }
}
```

## Health

### `GET /api/v1/health`

Response:

```json
{
  "status": "ok",
  "service": "Signal Tracker API",
  "environment": "development",
  "version": "0.1.0"
}
```

## Inbox

### `POST /api/v1/inbox/submit`

Request:

```json
{
  "url": "https://example.com/post",
  "title": "Optional title",
  "content": "Optional pasted text",
  "source_id": null
}
```

Response:

```json
{
  "success": true,
  "data": {
    "raw_item": {
      "id": 1,
      "title": "Optional title",
      "url": "https://example.com/post",
      "content": "Optional pasted text",
      "source_id": 1,
      "published_at": null,
      "captured_at": "2026-05-23T00:00:00Z"
    }
  },
  "error": null
}
```

### `GET /api/v1/inbox`

Query:

- `page`
- `page_size`
- `has_analysis`

Response data:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

## Extraction

### `POST /api/v1/raw-items/{raw_item_id}/analyze`

Response:

```json
{
  "success": true,
  "data": {
    "analysis": {
      "id": 1,
      "raw_item_id": 1,
      "summary": "Concise factual summary.",
      "signal_type": "hiring",
      "entities": [],
      "keywords": [],
      "claims": [],
      "suggested_tracking_queries": [],
      "novelty_score": 7.0,
      "relevance_score": 8.0,
      "credibility_hint": 5.0,
      "rationale": "Why this is a signal.",
      "model": "mock",
      "prompt_version": "signal_extract_v1"
    }
  },
  "error": null
}
```

## Intel Files

### `POST /api/v1/intel-files`

Create from analysis.

Request:

```json
{
  "raw_item_id": 1,
  "analysis_id": 1,
  "title": "Example AI hiring for hardware roles",
  "thesis": "This may indicate movement into AI hardware."
}
```

Response:

```json
{
  "success": true,
  "data": {
    "intel_file": {
      "id": 1,
      "title": "Example AI hiring for hardware roles",
      "thesis": "This may indicate movement into AI hardware.",
      "status": "new",
      "first_seen_at": "2026-05-23T00:00:00Z",
      "last_seen_at": "2026-05-23T00:00:00Z",
      "entities": [],
      "keywords": [],
      "evidence_count": 1,
      "source_count": 1,
      "novelty_score": 7.0,
      "heat_score": 1.0,
      "credibility_score": 5.0,
      "opportunity_score": 6.2,
      "risk_score": 2.0
    }
  },
  "error": null
}
```

### `GET /api/v1/intel-files`

Query:

- `page`
- `page_size`
- `status`
- `q`
- `min_opportunity`
- `sort`: `updated_desc`, `opportunity_desc`, `heat_desc`, `first_seen_desc`

### `GET /api/v1/intel-files/{id}`

Response includes:

- `intel_file`
- `evidence`
- `timeline`
- `snapshots`
- `alerts`

## Evidence

### `POST /api/v1/intel-files/{id}/evidence`

Request:

```json
{
  "raw_item_id": 2,
  "evidence_type": "follow_up",
  "confidence": 0.82,
  "rationale": "Same entity and claim; adds primary-source evidence."
}
```

Response:

```json
{
  "success": true,
  "data": {
    "evidence": {
      "id": 2,
      "intel_file_id": 1,
      "raw_item_id": 2,
      "evidence_type": "follow_up",
      "confidence": 0.82,
      "attached_by": "system",
      "rationale": "Same entity and claim; adds primary-source evidence."
    }
  },
  "error": null
}
```

### `GET /api/v1/intel-files/{id}/timeline`

Returns timeline events sorted ascending or descending.

## Lifecycle

### `POST /api/v1/intel-files/{id}/evaluate`

Request:

```json
{
  "reason": "manual",
  "now": null
}
```

Response:

```json
{
  "success": true,
  "data": {
    "previous_status": "dormant",
    "next_status": "resurrected",
    "reason": "New meaningful evidence appeared after dormancy.",
    "evidence_ids": [2],
    "score_changes": {
      "heat_score": [1.0, 5.5],
      "credibility_score": [4.0, 6.0]
    }
  },
  "error": null
}
```

## Scores

### `POST /api/v1/intel-files/{id}/score`

Runs scoring engine and stores a snapshot.

## Alerts

### `GET /api/v1/alerts`

Query:

- `status`
- `alert_type`
- `severity`

### `PATCH /api/v1/alerts/{id}`

Request:

```json
{
  "status": "acknowledged"
}
```

## Briefings

### `GET /api/v1/briefings/daily`

Query:

- `hours`: default 24
- `min_opportunity`: optional

Response:

```json
{
  "success": true,
  "data": {
    "meta": {
      "generated_at": "2026-05-23T00:00:00Z",
      "window_hours": 24,
      "item_count": 5
    },
    "sections": {
      "new_files": [],
      "updated_files": [],
      "resurrected": [],
      "high_opportunity": [],
      "risk_or_noise": []
    }
  },
  "error": null
}
```
