# Design

## API

- `GET /api/v1/workspaces/{workspace_id}/members`
- `POST /api/v1/workspaces/{workspace_id}/members`

The create endpoint accepts `email`, `name`, and `role`.

In production, adding members requires the caller to be an admin of the workspace. Listing members requires workspace membership.

## UI

The Workspace page shows:

- selected workspace members
- add-member form
- role selector

This is deliberately simple and does not send invitation emails.
