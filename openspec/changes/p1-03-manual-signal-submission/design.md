# Design: P1-03 Manual Signal Submission

## API

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/inbox/submit` | Create raw item from url/title/content |
| GET | `/api/v1/inbox` | List inbox items with analysis status |

Responses use the shared API envelope from `docs/specs/api-contracts.md`.

## Submission Rules

- At least one of `url`, `title`, or `content` is required.
- `content` may be null for URL-only intake.
- `content_hash` derived from normalized url and/or content.
- If `source_id` is omitted, associate with default manual source (get-or-create).
- Duplicate hash returns existing item with `duplicate: true`.

## Inbox Item Shape

Each list item includes:

- Raw item fields
- `analysis_status`: `pending` | `complete`
- `has_intel_file`: false in this task

## Frontend

- Inbox page: submission form + table list
- Calls backend via `NEXT_PUBLIC_API_BASE_URL`
- Shows readable errors from API envelope

## Module Layout

```text
backend/app/modules/inbox/service.py
backend/app/schemas/inbox.py
backend/app/schemas/api.py
backend/app/api/v1/inbox.py
apps/web/src/lib/api.ts
apps/web/src/components/inbox/*
```
