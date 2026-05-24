# TASK-P3-03: Status Override With Reason

## Goal

Let an analyst override an intel file lifecycle status while preserving an auditable reason in the timeline.

## Scope

- Add status override request/response schemas.
- Add backend service that updates status, writes lifecycle snapshot, writes status event, and triggers lifecycle alerts when relevant.
- Add API route on intel files.
- Add a compact override form on intel file detail.

## Acceptance

- Reason is required.
- Status changes are logged as timeline events.
- No-op overrides are accepted but explain that status was unchanged.
- Backend and frontend validation passes.
