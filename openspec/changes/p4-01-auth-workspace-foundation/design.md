# Design

Use local bootstrap auth for now:

- `POST /api/v1/auth/bootstrap`
- `GET /api/v1/workspaces`

Workspace scoping uses `X-Workspace-Id` for MVP. Real auth can later replace this with signed sessions/JWT.
