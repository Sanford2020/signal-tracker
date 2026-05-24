# TASK-P3-01: Accept Match Suggestions Into Evidence

## Goal

Close the review loop by letting an analyst accept a match suggestion and convert the source check result into attached evidence.

## Scope

- Add an acceptance service for open match suggestions.
- Create or reuse a RawItem from the source check result.
- Attach the RawItem as evidence to the target intel file.
- Mark the suggestion `accepted`.
- Add a UI button on intel file detail suggestions.

## Acceptance

- Accepted suggestions create exactly one evidence record.
- Re-accepting an already accepted suggestion is idempotent or returns the existing result safely.
- Suggestion status changes from `open` to `accepted`.
- Frontend refreshes detail/suggestions after acceptance.
