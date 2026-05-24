# Design

`ProviderBackedSourceChecker` delegates a tracking query to a provider selected by `source_hint`.

Providers return `CheckerResult` objects, which the existing runner persists as `SourceCheckResult` rows.

Default registry is empty and no-network for deterministic MVP operation.
