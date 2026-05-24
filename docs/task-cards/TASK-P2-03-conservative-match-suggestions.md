# TASK-P2-03: Conservative Match Suggestions

## Goal

Turn source check results into conservative evidence attachment suggestions without auto-attaching weak matches.

## Scope

- Add persisted match suggestions linked to intel files and source check results.
- Add a matcher service with deterministic scoring from title/thesis/entities/keywords against result title/snippet/url.
- Add API routes to generate suggestions for a source check run and list open suggestions for an intel file.
- Show suggestions on the intel file detail page.

## Acceptance

- Suggestions are only created above a configurable confidence threshold.
- Duplicate suggestions for the same intel file and source result are not recreated.
- Low-overlap results are ignored.
- Backend tests, migration smoke, and frontend type-check/build pass.
