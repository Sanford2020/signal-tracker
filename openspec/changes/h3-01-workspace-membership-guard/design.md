# Design

## Guard Behavior

`ensure_workspace_access` checks:

- workspace exists
- in non-production, return without membership enforcement
- in production, require `X-Workspace-Id`
- in production, require `X-User-Email`
- in production, require a matching `workspace_memberships` row

## Applied Routes

The guard is applied to workspace-scoped API surfaces:

- inbox
- intel file list/detail/create/evidence/collaboration/comments
- notification channels and deliveries
- usage summary
- source checks

## Boundary

This is still not full authentication. It is a production-mode authorization baseline using existing workspace membership data.
