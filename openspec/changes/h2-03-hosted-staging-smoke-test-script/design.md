# Design

`scripts/smoke-staging.ps1` accepts:

- `ApiBaseUrl`
- optional `WebBaseUrl`
- optional `AdminApiKey`

It checks:

- `GET /api/v1/health` returns `status=ok`
- backend response includes `X-Request-Id`
- bootstrap without `X-Admin-Secret` returns `401`
- bootstrap with `AdminApiKey` succeeds when provided
- frontend returns a 2xx response when provided

This script targets hosted staging URLs. It is separate from `validate-release.ps1`, which validates local code and build health.
