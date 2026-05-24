# Design

## Storage

`audit_events` stores:

- workspace id
- actor email
- action
- target type/id
- metadata
- timestamp

## API

`GET /api/v1/workspaces/{workspace_id}/audit-events` returns recent events and requires workspace admin access in production.

## UI

The Workspace page shows recent audit events for the selected workspace.
