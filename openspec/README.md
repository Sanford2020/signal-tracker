# OpenSpec Layer

This directory is a lightweight OpenSpec-inspired execution layer for Signal Tracker.

It does not replace the project planning docs. It adds a change-by-change workflow for AI employees.

## Structure

```text
openspec/
  specs/      Current agreed behavior, grouped by domain
  changes/    Proposed implementation changes, one folder per change
```

## How To Use

1. Read the relevant current spec under `openspec/specs/`.
2. Work from one change folder under `openspec/changes/`.
3. Follow that change's `proposal.md`, `design.md`, and `tasks.md`.
4. Verify implementation against scenarios.
5. After completion, archive or merge the change into current specs.

## Relationship To Project Docs

| Layer | Files |
| --- | --- |
| Strategy | `PROJECT_BRIEF.md`, `docs/prd.md`, `docs/commercial-prd.md` |
| Methodology | `docs/methodology/*` |
| Architecture | `docs/architecture/*`, `DECISIONS.md` |
| Execution | `openspec/changes/*`, `docs/task-cards/*` |
| Current behavior | `openspec/specs/*` |

## Rule

Every implementation task should have a change folder before code starts.
