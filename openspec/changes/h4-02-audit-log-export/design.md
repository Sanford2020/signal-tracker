# Design

## API

`GET /api/v1/workspaces/{workspace_id}/audit-events.csv`

Requires workspace admin access in production and returns `text/csv`.

## CSV Fields

- `created_at`
- `actor_email`
- `action`
- `target_type`
- `target_id`
- `metadata`

## Frontend

The Workspace page uses `fetch` so token headers are included, then downloads the response as a Blob.
