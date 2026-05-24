import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from typing import Protocol

import httpx

from app.core.config import get_settings
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


class GitHubReleasesProvider:
    """Search recent GitHub releases for repository-shaped tracking queries."""

    api_base_url = "https://api.github.com"
    repo_pattern = re.compile(r"(?<![\w.-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?![\w.-])")

    def __init__(
        self,
        *,
        token: str | None = None,
        client: httpx.Client | None = None,
        max_repositories: int = 3,
        max_releases_per_repo: int = 2,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.token = token
        self.client = client
        self.max_repositories = max(1, max_repositories)
        self.max_releases_per_repo = max(1, max_releases_per_repo)
        self.timeout_seconds = timeout_seconds

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        repo_names = self._repo_names_for_query(query.query)
        if not repo_names:
            repo_names = self._search_repositories(query.query)
        results: list[CheckerResult] = []
        for repo_name in repo_names[: self.max_repositories]:
            results.extend(self._latest_releases(repo_name))
        return results

    def _request(self, path: str, params: dict[str, str | int] | None = None) -> httpx.Response:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "signal-tracker-source-provider",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if self.client is not None:
            return self.client.get(path, params=params, headers=headers)

        with httpx.Client(base_url=self.api_base_url, timeout=self.timeout_seconds) as client:
            return client.get(path, params=params, headers=headers)

    def _repo_names_for_query(self, query: str) -> list[str]:
        seen: set[str] = set()
        names: list[str] = []
        for match in self.repo_pattern.finditer(query):
            repo = match.group(1)
            normalized = repo.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            names.append(repo)
        return names

    def _search_repositories(self, query: str) -> list[str]:
        response = self._request(
            "/search/repositories",
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": self.max_repositories,
            },
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", []) if isinstance(payload, dict) else []
        names: list[str] = []
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("full_name"), str):
                names.append(item["full_name"])
        return names

    def _latest_releases(self, repo_name: str) -> list[CheckerResult]:
        response = self._request(
            f"/repos/{repo_name}/releases",
            params={"per_page": self.max_releases_per_repo},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return []

        results: list[CheckerResult] = []
        for item in payload[: self.max_releases_per_repo]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("name") or item.get("tag_name") or f"{repo_name} release")
            url = item.get("html_url")
            body = item.get("body")
            published_at = item.get("published_at")
            results.append(
                CheckerResult(
                    title=f"{repo_name}: {title}",
                    url=str(url) if url else None,
                    snippet=str(body)[:500] if body else None,
                    source_name="github-releases",
                    raw={
                        "provider": "github_releases",
                        "repo": repo_name,
                        "tag_name": item.get("tag_name"),
                        "published_at": published_at,
                    },
                )
            )
        return results


class RssFeedProvider:
    """Search configured RSS/Atom feeds for query-relevant entries."""

    token_pattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,}")

    def __init__(
        self,
        feed_urls: Sequence[str],
        *,
        client: httpx.Client | None = None,
        max_entries_per_feed: int = 20,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.feed_urls = list(feed_urls)
        self.client = client
        self.max_entries_per_feed = max(1, max_entries_per_feed)
        self.timeout_seconds = timeout_seconds

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        if not self.feed_urls:
            return []

        tokens = self._tokens(query.query)
        results: list[CheckerResult] = []
        for feed_url in self.feed_urls:
            response = self._request(feed_url)
            response.raise_for_status()
            results.extend(self._results_from_xml(feed_url, response.text, tokens))
        return results

    def _request(self, feed_url: str) -> httpx.Response:
        headers = {"User-Agent": "signal-tracker-rss-provider"}
        if self.client is not None:
            return self.client.get(feed_url, headers=headers)
        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True) as client:
            return client.get(feed_url, headers=headers)

    def _tokens(self, query: str) -> set[str]:
        return {match.group(0).lower() for match in self.token_pattern.finditer(query)}

    def _results_from_xml(self, feed_url: str, xml_text: str, tokens: set[str]) -> list[CheckerResult]:
        root = ET.fromstring(xml_text)
        entries = list(root.findall(".//item"))
        entries.extend(root.findall(".//{http://www.w3.org/2005/Atom}entry"))

        results: list[CheckerResult] = []
        for entry in entries[: self.max_entries_per_feed]:
            title = self._text(entry, "title") or "Untitled feed entry"
            link = self._link(entry)
            snippet = self._text(entry, "description") or self._text(entry, "summary") or self._text(entry, "content")
            haystack = f"{title} {snippet or ''}".lower()
            if tokens and not any(token in haystack for token in tokens):
                continue
            results.append(
                CheckerResult(
                    title=title,
                    url=link,
                    snippet=snippet[:500] if snippet else None,
                    source_name="rss-feed",
                    raw={
                        "provider": "rss_feed",
                        "feed_url": feed_url,
                        "published_at": self._text(entry, "pubDate") or self._text(entry, "updated"),
                    },
                )
            )
        return results

    def _text(self, entry: ET.Element, name: str) -> str | None:
        candidates = [
            entry.find(name),
            entry.find(f"{{http://www.w3.org/2005/Atom}}{name}"),
            entry.find(f"{{http://purl.org/rss/1.0/}}{name}"),
        ]
        for candidate in candidates:
            if candidate is not None and candidate.text and candidate.text.strip():
                return candidate.text.strip()
        return None

    def _link(self, entry: ET.Element) -> str | None:
        text_link = self._text(entry, "link")
        if text_link:
            return text_link
        atom_link = entry.find("{http://www.w3.org/2005/Atom}link")
        href = atom_link.attrib.get("href") if atom_link is not None else None
        return href.strip() if href else None


def get_default_provider_registry() -> SourceProviderRegistry:
    settings = get_settings()
    github_provider = GitHubReleasesProvider(
        token=settings.github_api_token,
        max_repositories=settings.github_provider_max_repositories,
        max_releases_per_repo=settings.github_provider_max_releases_per_repo,
        timeout_seconds=settings.github_provider_timeout_seconds,
    )
    rss_provider = RssFeedProvider(
        settings.rss_feed_url_list,
        max_entries_per_feed=settings.rss_provider_max_entries_per_feed,
        timeout_seconds=settings.rss_provider_timeout_seconds,
    )
    return SourceProviderRegistry(
        {
            "github": github_provider,
            "github_releases": github_provider,
            "rss": rss_provider,
            "news": rss_provider,
            "search": rss_provider,
        }
    )
