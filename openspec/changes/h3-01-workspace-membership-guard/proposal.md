# H3-01 Workspace Membership Guard

Render staging can expose the app to a public URL. The app already has workspaces and memberships, but many workspace-scoped routes still trust `X-Workspace-Id` alone.

This change adds a production-mode membership guard so a caller must provide a user email that belongs to the target workspace.
