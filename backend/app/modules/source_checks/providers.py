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


class CompositeSourceProvider:
    def __init__(self, providers: Sequence[SourceProvider]) -> None:
        self.providers = list(providers)

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        results: list[CheckerResult] = []
        for provider in self.providers:
            results.extend(provider.search(query))
        return results


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


class GitHubActivityProvider:
    """Search recent GitHub issues and commits for repository-shaped tracking queries."""

    api_base_url = "https://api.github.com"
    repo_pattern = GitHubReleasesProvider.repo_pattern

    def __init__(
        self,
        *,
        token: str | None = None,
        client: httpx.Client | None = None,
        max_repositories: int = 3,
        max_items_per_repo: int = 2,
        timeout_seconds: float = 10.0,
        include_issues: bool = True,
        include_commits: bool = True,
    ) -> None:
        self.token = token
        self.client = client
        self.max_repositories = max(1, max_repositories)
        self.max_items_per_repo = max(1, max_items_per_repo)
        self.timeout_seconds = timeout_seconds
        self.include_issues = include_issues
        self.include_commits = include_commits

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        repo_names = self._repo_names_for_query(query.query)
        if not repo_names:
            repo_names = self._search_repositories(query.query)

        results: list[CheckerResult] = []
        for repo_name in repo_names[: self.max_repositories]:
            if self.include_issues:
                results.extend(self._latest_issues(repo_name))
            if self.include_commits:
                results.extend(self._latest_commits(repo_name))
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

    def _latest_issues(self, repo_name: str) -> list[CheckerResult]:
        response = self._request(
            f"/repos/{repo_name}/issues",
            params={
                "state": "all",
                "sort": "updated",
                "direction": "desc",
                "per_page": self.max_items_per_repo,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return []

        results: list[CheckerResult] = []
        for item in payload[: self.max_items_per_repo]:
            if not isinstance(item, dict) or item.get("pull_request"):
                continue
            number = item.get("number")
            title = str(item.get("title") or f"{repo_name} issue")
            url = item.get("html_url")
            body = item.get("body")
            updated_at = item.get("updated_at")
            results.append(
                CheckerResult(
                    title=f"{repo_name}: issue #{number} {title}",
                    url=str(url) if url else None,
                    snippet=str(body)[:500] if body else None,
                    source_name="github-issues",
                    raw={
                        "provider": "github_issues",
                        "repo": repo_name,
                        "number": number,
                        "state": item.get("state"),
                        "updated_at": updated_at,
                    },
                )
            )
        return results

    def _latest_commits(self, repo_name: str) -> list[CheckerResult]:
        response = self._request(f"/repos/{repo_name}/commits", params={"per_page": self.max_items_per_repo})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return []

        results: list[CheckerResult] = []
        for item in payload[: self.max_items_per_repo]:
            if not isinstance(item, dict):
                continue
            commit = item.get("commit") if isinstance(item.get("commit"), dict) else {}
            message = str(commit.get("message") or f"{repo_name} commit").splitlines()[0]
            author = commit.get("author") if isinstance(commit.get("author"), dict) else {}
            sha = item.get("sha")
            url = item.get("html_url")
            results.append(
                CheckerResult(
                    title=f"{repo_name}: commit {message}",
                    url=str(url) if url else None,
                    snippet=str(commit.get("message"))[:500] if commit.get("message") else None,
                    source_name="github-commits",
                    raw={
                        "provider": "github_commits",
                        "repo": repo_name,
                        "sha": str(sha) if sha else None,
                        "committed_at": author.get("date"),
                    },
                )
            )
        return results


class ArxivProvider:
    """Search arXiv Atom API for recent research papers matching a tracking query."""

    api_base_url = "https://export.arxiv.org"
    atom_namespace = {"atom": "http://www.w3.org/2005/Atom"}

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        max_results: int = 10,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.client = client
        self.max_results = max(1, min(max_results, 50))
        self.timeout_seconds = timeout_seconds

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        response = self._request(
            "/api/query",
            params={
                "search_query": f"all:{query.query}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": self.max_results,
            },
        )
        response.raise_for_status()
        return self._results_from_atom(response.text)

    def _request(self, path: str, params: dict[str, str | int]) -> httpx.Response:
        headers = {"User-Agent": "signal-tracker-arxiv-provider"}
        if self.client is not None:
            return self.client.get(path, params=params, headers=headers)
        with httpx.Client(base_url=self.api_base_url, timeout=self.timeout_seconds) as client:
            return client.get(path, params=params, headers=headers)

    def _results_from_atom(self, xml_text: str) -> list[CheckerResult]:
        root = ET.fromstring(xml_text)
        entries = root.findall("atom:entry", self.atom_namespace)
        results: list[CheckerResult] = []
        for entry in entries[: self.max_results]:
            paper_id = self._text(entry, "id")
            title = self._text(entry, "title") or "Untitled arXiv paper"
            summary = self._text(entry, "summary")
            published_at = self._text(entry, "published")
            updated_at = self._text(entry, "updated")
            authors = [
                name.text.strip()
                for name in entry.findall("atom:author/atom:name", self.atom_namespace)
                if name.text and name.text.strip()
            ]
            categories = [
                category.attrib["term"]
                for category in entry.findall("atom:category", self.atom_namespace)
                if category.attrib.get("term")
            ]
            results.append(
                CheckerResult(
                    title=title,
                    url=self._link(entry) or paper_id,
                    snippet=summary[:500] if summary else None,
                    source_name="arxiv",
                    raw={
                        "provider": "arxiv",
                        "arxiv_id": paper_id.rsplit("/", 1)[-1] if paper_id else None,
                        "published_at": published_at,
                        "updated_at": updated_at,
                        "authors": authors,
                        "categories": categories,
                    },
                )
            )
        return results

    def _text(self, entry: ET.Element, name: str) -> str | None:
        element = entry.find(f"atom:{name}", self.atom_namespace)
        if element is not None and element.text and element.text.strip():
            return re.sub(r"\s+", " ", element.text.strip())
        return None

    def _link(self, entry: ET.Element) -> str | None:
        preferred: str | None = None
        fallback: str | None = None
        for link in entry.findall("atom:link", self.atom_namespace):
            href = link.attrib.get("href")
            if not href:
                continue
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                preferred = href.strip()
            elif fallback is None:
                fallback = href.strip()
        return preferred or fallback


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


class HackerNewsProvider:
    """Search HN Search by Algolia for early technical/product chatter."""

    api_base_url = "https://hn.algolia.com"

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        max_hits: int = 10,
        timeout_seconds: float = 10.0,
        tags: str = "story",
    ) -> None:
        self.client = client
        self.max_hits = max(1, min(max_hits, 50))
        self.timeout_seconds = timeout_seconds
        self.tags = tags

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        response = self._request(
            "/api/v1/search_by_date",
            params={
                "query": query.query,
                "tags": self.tags,
                "hitsPerPage": self.max_hits,
            },
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload.get("hits", []) if isinstance(payload, dict) else []
        results: list[CheckerResult] = []
        for hit in hits[: self.max_hits]:
            if not isinstance(hit, dict):
                continue
            title = hit.get("title") or hit.get("story_title")
            object_id = hit.get("objectID") or hit.get("story_id")
            if not title or not object_id:
                continue
            url = hit.get("url") or hit.get("story_url") or f"https://news.ycombinator.com/item?id={object_id}"
            snippet = hit.get("story_text") or hit.get("comment_text")
            results.append(
                CheckerResult(
                    title=str(title),
                    url=str(url),
                    snippet=str(snippet)[:500] if snippet else None,
                    source_name="hacker-news",
                    raw={
                        "provider": "hacker_news",
                        "object_id": str(object_id),
                        "author": hit.get("author"),
                        "points": hit.get("points"),
                        "num_comments": hit.get("num_comments"),
                        "created_at": hit.get("created_at"),
                    },
                )
            )
        return results

    def _request(self, path: str, params: dict[str, str | int]) -> httpx.Response:
        headers = {"User-Agent": "signal-tracker-hacker-news-provider"}
        if self.client is not None:
            return self.client.get(path, params=params, headers=headers)
        with httpx.Client(base_url=self.api_base_url, timeout=self.timeout_seconds) as client:
            return client.get(path, params=params, headers=headers)


class PyPIPackageProvider:
    """Check PyPI package metadata for recent Python package release signals."""

    api_base_url = "https://pypi.org"
    package_pattern = re.compile(r"(?<![\w.-])([A-Za-z0-9][A-Za-z0-9_.-]{1,80})(?![\w.-])")
    stopwords = {
        "about",
        "agent",
        "agents",
        "check",
        "follow",
        "latest",
        "package",
        "packages",
        "python",
        "release",
        "releases",
        "sdk",
        "track",
        "update",
        "watch",
    }

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        max_packages: int = 5,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.client = client
        self.max_packages = max(1, min(max_packages, 20))
        self.timeout_seconds = timeout_seconds

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        results: list[CheckerResult] = []
        for package_name in self._package_names_for_query(query.query):
            payload = self._package_json(package_name)
            if payload is None:
                continue
            result = self._result_from_payload(package_name, payload)
            if result is not None:
                results.append(result)
        return results

    def _request(self, package_name: str) -> httpx.Response:
        headers = {"User-Agent": "signal-tracker-pypi-provider"}
        path = f"/pypi/{package_name}/json"
        if self.client is not None:
            return self.client.get(path, headers=headers)
        with httpx.Client(base_url=self.api_base_url, timeout=self.timeout_seconds) as client:
            return client.get(path, headers=headers)

    def _package_names_for_query(self, query: str) -> list[str]:
        seen: set[str] = set()
        names: list[str] = []
        for match in self.package_pattern.finditer(query):
            name = match.group(1).strip("._-").lower()
            if not name or name in self.stopwords or name in seen:
                continue
            seen.add(name)
            names.append(name)
            if len(names) >= self.max_packages:
                break
        return names

    def _package_json(self, package_name: str) -> dict | None:
        response = self._request(package_name)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else None

    def _result_from_payload(self, package_name: str, payload: dict) -> CheckerResult | None:
        info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
        version = info.get("version")
        if not isinstance(version, str) or not version:
            return None

        project_name = str(info.get("name") or package_name)
        summary = info.get("summary")
        project_url = info.get("project_url")
        if not isinstance(project_url, str) or not project_url:
            project_url = f"https://pypi.org/project/{project_name}/"

        release_files = []
        releases = payload.get("releases")
        if isinstance(releases, dict):
            maybe_files = releases.get(version)
            if isinstance(maybe_files, list):
                release_files = [item for item in maybe_files if isinstance(item, dict)]

        upload_time = None
        if release_files:
            upload_time = release_files[0].get("upload_time_iso_8601") or release_files[0].get("upload_time")

        return CheckerResult(
            title=f"{project_name} {version} released on PyPI",
            url=project_url,
            snippet=str(summary)[:500] if summary else None,
            source_name="pypi",
            raw={
                "provider": "pypi",
                "package": project_name,
                "version": version,
                "upload_time": upload_time,
            },
        )


def get_default_provider_registry() -> SourceProviderRegistry:
    settings = get_settings()
    github_provider = GitHubReleasesProvider(
        token=settings.github_api_token,
        max_repositories=settings.github_provider_max_repositories,
        max_releases_per_repo=settings.github_provider_max_releases_per_repo,
        timeout_seconds=settings.github_provider_timeout_seconds,
    )
    github_activity_provider = GitHubActivityProvider(
        token=settings.github_api_token,
        max_repositories=settings.github_provider_max_repositories,
        max_items_per_repo=settings.github_provider_max_activity_items_per_repo,
        timeout_seconds=settings.github_provider_timeout_seconds,
    )
    github_issues_provider = GitHubActivityProvider(
        token=settings.github_api_token,
        max_repositories=settings.github_provider_max_repositories,
        max_items_per_repo=settings.github_provider_max_activity_items_per_repo,
        timeout_seconds=settings.github_provider_timeout_seconds,
        include_commits=False,
    )
    github_commits_provider = GitHubActivityProvider(
        token=settings.github_api_token,
        max_repositories=settings.github_provider_max_repositories,
        max_items_per_repo=settings.github_provider_max_activity_items_per_repo,
        timeout_seconds=settings.github_provider_timeout_seconds,
        include_issues=False,
    )
    rss_provider = RssFeedProvider(
        settings.rss_feed_url_list,
        max_entries_per_feed=settings.rss_provider_max_entries_per_feed,
        timeout_seconds=settings.rss_provider_timeout_seconds,
    )
    arxiv_provider = ArxivProvider(
        max_results=settings.arxiv_provider_max_results,
        timeout_seconds=settings.arxiv_provider_timeout_seconds,
    )
    hacker_news_provider = HackerNewsProvider(
        max_hits=settings.hacker_news_provider_max_hits,
        timeout_seconds=settings.hacker_news_provider_timeout_seconds,
        tags=settings.hacker_news_provider_tags,
    )
    pypi_provider = PyPIPackageProvider(
        max_packages=settings.pypi_provider_max_packages,
        timeout_seconds=settings.pypi_provider_timeout_seconds,
    )
    return SourceProviderRegistry(
        {
            "github": CompositeSourceProvider([github_provider, github_activity_provider]),
            "github_releases": github_provider,
            "github_activity": github_activity_provider,
            "github_issues": github_issues_provider,
            "github_commits": github_commits_provider,
            "rss": rss_provider,
            "news": rss_provider,
            "research": arxiv_provider,
            "arxiv": arxiv_provider,
            "paper": arxiv_provider,
            "papers": arxiv_provider,
            "search": hacker_news_provider,
            "careers": hacker_news_provider,
            "hacker_news": hacker_news_provider,
            "hiring": hacker_news_provider,
            "hn": hacker_news_provider,
            "jobs": hacker_news_provider,
            "package": pypi_provider,
            "pypi": pypi_provider,
            "python_package": pypi_provider,
            "sdk": pypi_provider,
            "social": hacker_news_provider,
        }
    )
