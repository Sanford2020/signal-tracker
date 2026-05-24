# TASK-P3-02: Source Provider Framework

## Goal

Make source checks extensible through provider adapters instead of hardcoding checker behavior.

## Scope

- Add provider protocol and registry.
- Route tracking queries to providers by `source_hint`.
- Keep default behavior deterministic and no-network.
- Add tests proving configured providers produce source check results through the existing runner.

## Acceptance

- A registered provider can return results for matching `source_hint`.
- Missing providers do not fail a run.
- Provider exceptions are isolated to the affected query and recorded by the runner.
