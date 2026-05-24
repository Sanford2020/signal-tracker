# Design

`trend_archive_snapshots` stores one row per `intel_file_id` and archive date.

The archive worker captures:

- lifecycle status
- heat, credibility, opportunity, and risk scores
- evidence count
- source count
- last seen timestamp

`POST /api/v1/archives/snapshots/run` creates or updates snapshots.
`GET /api/v1/intel-files/{id}/trend` returns chronological snapshots.
