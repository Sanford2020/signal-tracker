# Design

## Token Lifecycle

- Bootstrap issues an access token for the bootstrap user.
- Adding a workspace member issues or rotates that user's access token.
- The API returns the plaintext token once.
- The database stores `access_token_hash` and `access_token_hint`.

## Request Guard

Production workspace-scoped routes require:

- `X-Workspace-Id`
- `X-User-Email`
- `X-User-Token`

The token is SHA-256 hashed and compared with `secrets.compare_digest`.

## Boundary

This is a staging access-control baseline. Customer production still needs real authentication, session management, passwordless login, SSO, or another proper identity provider.
