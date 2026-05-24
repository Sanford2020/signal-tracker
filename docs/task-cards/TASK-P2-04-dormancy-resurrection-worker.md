# TASK-P2-04: Dormancy and Resurrection Worker

## Goal

Run lifecycle checks in batch so stale files become dormant and dormant files with meaningful new evidence resurrect without manual per-file evaluation.

## Scope

- Add a worker-style service that scans lifecycle candidates.
- Reuse the existing lifecycle evaluation rules and alert creation.
- Add an API endpoint to trigger the worker manually for MVP operations.
- Add tests for dormancy, resurrection, limits, and no-op runs.

## Acceptance

- Active stale files transition to `dormant`.
- Dormant files with recent non-first-seen evidence transition to `resurrected`.
- Resurrection alerts are created through the existing alert service.
- Worker reports checked and transitioned files.
