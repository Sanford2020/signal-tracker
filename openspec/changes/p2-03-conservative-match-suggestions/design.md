# Design

## Data

`match_suggestions` stores an intel file, source check result, suggested evidence type, confidence, rationale, status, and decision timestamp.

## Matching

The matcher uses the `SourceCheckResult -> TrackingQuery -> IntelFile` path as the candidate file, then scores overlap between source result text and file terms:

- title terms
- thesis terms
- keywords
- entity names
- tracking query terms

The initial threshold defaults to `0.65`. Results below threshold are ignored.

## API

- `POST /api/v1/source-checks/runs/{run_id}/match-suggestions`
- `GET /api/v1/intel-files/{intel_file_id}/match-suggestions`
