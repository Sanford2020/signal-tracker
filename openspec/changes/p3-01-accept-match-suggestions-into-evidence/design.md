# Design

## Flow

1. Load an open `MatchSuggestion`.
2. Convert its `SourceCheckResult` into a `RawItem` under a system source.
3. Attach that raw item to the suggestion's intel file as follow-up evidence.
4. Mark the suggestion accepted.

The service should reuse existing `attach_evidence` behavior so evidence counts, timeline events, source counts, and `last_seen_at` are updated consistently.
