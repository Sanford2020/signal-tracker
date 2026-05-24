# TASK-P3-04: Trend Archive Snapshots

## Goal

Persist daily archive snapshots for intel files so later trend review and weekly retrospectives can compare status, scores, and evidence growth over time.

## Scope

- Add a daily `TrendArchiveSnapshot` table.
- Add a worker service that snapshots current intel file state for a target date.
- Make snapshots idempotent per file and date.
- Add API endpoints to run snapshots and list a file's trend history.

## Acceptance

- Running the archive worker creates one snapshot per intel file for the date.
- Re-running for the same date updates existing snapshots instead of duplicating rows.
- File trend API returns snapshots in chronological order.
- Migration smoke and backend tests pass.
