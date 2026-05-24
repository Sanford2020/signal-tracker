# Design

## Worker

The worker selects:

- non-terminal files older than the configured dormancy window
- dormant or archived files that need resurrection checks

It delegates decisions to the existing lifecycle evaluator so status changes, snapshots, events, and alerts stay consistent.

## API

`POST /api/v1/lifecycle/run`

The endpoint is intentionally manual for MVP. A scheduler can call the same service later.
