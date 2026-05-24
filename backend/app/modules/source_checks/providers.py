from collections.abc import Mapping, Sequence
from typing import Protocol

from app.models import TrackingQuery
from app.modules.source_checks.service import CheckerResult, SourceChecker


class SourceProvider(Protocol):
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        """Return provider-specific results for a tracking query."""


class SourceProviderRegistry:
    def __init__(self, providers: Mapping[str, SourceProvider] | None = None) -> None:
        self._providers = dict(providers or {})

    def register(self, source_hint: str, provider: SourceProvider) -> None:
        self._providers[source_hint] = provider

    def get(self, source_hint: str | None) -> SourceProvider | None:
        if not source_hint:
            return None
        return self._providers.get(source_hint)


class ProviderBackedSourceChecker(SourceChecker):
    def __init__(self, registry: SourceProviderRegistry) -> None:
        self.registry = registry

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        provider = self.registry.get(query.source_hint)
        if provider is None:
            return []
        return provider.search(query)


def get_default_provider_registry() -> SourceProviderRegistry:
    return SourceProviderRegistry()
