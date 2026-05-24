# Design

`scripts/check-env-readiness.ps1` parses a dotenv-style file and validates required values.

Production mode checks:

- required backend/frontend keys
- `ADMIN_API_KEY`
- non-default database credentials
- explicit non-wildcard origins
- non-local frontend API base URL
- AI key only when live AI mode is enabled

The script does not connect to any external service.
