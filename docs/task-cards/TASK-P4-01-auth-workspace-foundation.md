# TASK-P4-01: Auth and Workspace Foundation

## Goal

Add a minimal commercial foundation for users and workspace-scoped data without forcing third-party OAuth in the MVP.

## Scope

- Add users, workspaces, and workspace memberships.
- Add bootstrap/login-style endpoint for local development.
- Allow inbox submission and intel file listing/detail to scope by `X-Workspace-Id`.
- Add a small frontend workspace page to create/select the demo workspace context.

## Acceptance

- A user can bootstrap a workspace.
- New raw items and intel files can be assigned to a workspace.
- Workspace-scoped intel file listing does not leak files from another workspace.
- Existing no-auth MVP flows continue to work.
