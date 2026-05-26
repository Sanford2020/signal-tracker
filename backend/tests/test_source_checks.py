from collections.abc import Sequence
from uuid import UUID
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.models import SourceCheckResult, SourceCheckRun, TrackingQuery
from app.modules.source_checks.providers import (
    ArxivProvider,
    CompositeSourceProvider,
    GitHubActivityProvider,
    GitHubReleasesProvider,
    HackerNewsProvider,
    ProviderBackedSourceChecker,
    RssFeedProvider,
    SourceProviderRegistry,
    get_default_provider_registry,
)
from app.modules.source_checks.service import CheckerResult, run_source_checks
from app.schemas.source_checks import SourceCheckRunRequest


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def _create_tracking_queries(client: TestClient) -> list[dict]:
    submit = client.post(
        "/api/v1/inbox/submit",
        json={
            "title": "Northstar AI posts robotics procurement role",
            "content": "Northstar AI is hiring robotics procurement and supply chain operators.",
        },
    )
    assert submit.status_code == 200
    raw_item_id = submit.json()["data"]["raw_item"]["id"]
    assert client.post(f"/api/v1/raw-items/{raw_item_id}/analyze").status_code == 200
    create_file = client.post("/api/v1/intel-files", json={"raw_item_id": raw_item_id})
    assert create_file.status_code == 200
    intel_file_id = create_file.json()["data"]["intel_file"]["id"]

    generated = client.post(f"/api/v1/intel-files/{intel_file_id}/tracking-queries", json={"limit": 4})
    assert generated.status_code == 200
    return generated.json()["data"]["items"]


class RecordingChecker:
    def __init__(self) -> None:
        self.seen: list[str] = []

    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        self.seen.append(query.query)
        return [
            CheckerResult(
                title=f"Follow-up for {query.query}",
                url=f"https://example.com/{query.id}",
                snippet="A fresh follow-up item was found.",
                source_name="example-search",
                raw={"query": query.query},
            )
        ]


class FailingChecker:
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        raise RuntimeError("provider unavailable")


def test_api_run_source_checks_consumes_enabled_queries(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.api.v1.source_checks.get_default_provider_registry",
        lambda: SourceProviderRegistry(),
    )
    _create_tracking_queries(client)
    response = client.post("/api/v1/source-checks/run", json={"limit": 2})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["run"]["status"] == "completed"
    assert data["run"]["checked_query_count"] == 2
    assert data["run"]["result_count"] == 0
    assert data["results"] == []

    stored_run = db_session.scalar(select(SourceCheckRun))
    assert stored_run is not None
    assert stored_run.checked_query_count == 2


def test_api_lists_recent_source_check_runs(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.source_checks.get_default_provider_registry",
        lambda: SourceProviderRegistry(),
    )
    _create_tracking_queries(client)
    run = client.post("/api/v1/source-checks/run", json={"limit": 2})
    assert run.status_code == 200

    response = client.get("/api/v1/source-checks/runs?limit=5")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["checked_query_count"] == 2


def test_api_summarizes_source_provider_health(client: TestClient, db_session: Session) -> None:
    _create_tracking_queries(client)
    query = db_session.scalar(select(TrackingQuery))
    assert query is not None
    query.source_hint = "search"
    db_session.commit()
    run_source_checks(db_session, SourceCheckRunRequest(limit=2), checker=RecordingChecker())

    response = client.get("/api/v1/source-checks/provider-health?limit=10")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1
    search_item = next(item for item in data["items"] if item["source_hint"] == "search")
    assert search_item["enabled_query_count"] >= 1
    assert search_item["recent_result_count"] >= 1
    assert search_item["last_result_at"] is not None
    assert search_item["latest_run_status"] == "completed"
    assert search_item["latest_run_error"] is None


def test_run_source_checks_persists_results(client: TestClient, db_session: Session) -> None:
    _create_tracking_queries(client)
    checker = RecordingChecker()

    data = run_source_checks(db_session, SourceCheckRunRequest(limit=2), checker=checker)

    assert data.run.status == "completed"
    assert data.run.checked_query_count == 2
    assert data.run.result_count == 2
    assert len(data.results) == 2
    assert len(checker.seen) == 2
    persisted = db_session.scalars(select(SourceCheckResult)).all()
    assert len(persisted) == 2
    assert persisted[0].source_name == "example-search"


def test_disabled_tracking_queries_are_skipped(client: TestClient, db_session: Session) -> None:
    generated = _create_tracking_queries(client)
    disabled_id = generated[0]["id"]
    query = db_session.get(TrackingQuery, UUID(disabled_id))
    assert query is not None
    query.enabled = False
    db_session.commit()

    checker = RecordingChecker()
    data = run_source_checks(db_session, SourceCheckRunRequest(limit=10), checker=checker)

    assert data.run.checked_query_count == len(generated) - 1
    assert query.query not in checker.seen


def test_checker_failures_are_recorded(client: TestClient, db_session: Session) -> None:
    _create_tracking_queries(client)

    data = run_source_checks(db_session, SourceCheckRunRequest(limit=1), checker=FailingChecker())

    assert data.run.status == "failed"
    assert data.run.checked_query_count == 1
    assert data.run.result_count == 0
    assert data.run.error is not None
    assert "provider unavailable" in data.run.error


class CareersProvider:
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        return [
            CheckerResult(
                title=f"Provider result for {query.query}",
                url="https://example.com/provider-result",
                snippet="Configured provider returned this result.",
                source_name="careers-provider",
            )
        ]


class ExplodingProvider:
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        raise RuntimeError("provider exploded")


def test_provider_backed_checker_routes_by_source_hint(
    client: TestClient,
    db_session: Session,
) -> None:
    _create_tracking_queries(client)
    query = db_session.scalar(select(TrackingQuery))
    assert query is not None
    query.source_hint = "careers"
    db_session.commit()
    registry = SourceProviderRegistry({"careers": CareersProvider()})
    checker = ProviderBackedSourceChecker(registry)

    data = run_source_checks(db_session, SourceCheckRunRequest(limit=10), checker=checker)

    assert data.run.status == "completed"
    assert data.run.result_count >= 1
    assert any(item.source_name == "careers-provider" for item in data.results)


def test_provider_backed_checker_missing_provider_is_noop(
    client: TestClient,
    db_session: Session,
) -> None:
    _create_tracking_queries(client)
    checker = ProviderBackedSourceChecker(SourceProviderRegistry())

    data = run_source_checks(db_session, SourceCheckRunRequest(limit=10), checker=checker)

    assert data.run.status == "completed"
    assert data.run.result_count == 0


def test_provider_backed_checker_failures_are_recorded(
    client: TestClient,
    db_session: Session,
) -> None:
    _create_tracking_queries(client)
    query = db_session.scalar(select(TrackingQuery))
    assert query is not None
    query.source_hint = "careers"
    db_session.commit()
    registry = SourceProviderRegistry({"careers": ExplodingProvider()})
    checker = ProviderBackedSourceChecker(registry)

    data = run_source_checks(db_session, SourceCheckRunRequest(limit=10), checker=checker)

    assert data.run.status in {"failed", "partial"}
    assert data.run.error is not None
    assert "provider exploded" in data.run.error


def test_github_releases_provider_returns_recent_releases_for_repo_query() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/repos/huggingface/transformers/releases"
        return httpx.Response(
            200,
            json=[
                {
                    "name": "v5.0.0",
                    "tag_name": "v5.0.0",
                    "html_url": "https://github.com/huggingface/transformers/releases/tag/v5.0.0",
                    "body": "Major release notes",
                    "published_at": "2026-05-24T00:00:00Z",
                }
            ],
        )

    client = httpx.Client(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    provider = GitHubReleasesProvider(client=client, max_releases_per_repo=1)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="Watch huggingface/transformers releases",
        normalized_query="watch huggingface/transformers releases",
        source_hint="github",
    )

    results = provider.search(query)

    assert len(results) == 1
    assert results[0].title == "huggingface/transformers: v5.0.0"
    assert results[0].source_name == "github-releases"
    assert results[0].raw == {
        "provider": "github_releases",
        "repo": "huggingface/transformers",
        "tag_name": "v5.0.0",
        "published_at": "2026-05-24T00:00:00Z",
    }


def test_github_releases_provider_searches_repositories_when_no_repo_slug() -> None:
    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path == "/search/repositories":
            return httpx.Response(200, json={"items": [{"full_name": "openai/openai-python"}]})
        if request.url.path == "/repos/openai/openai-python/releases":
            return httpx.Response(
                200,
                json=[
                    {
                        "name": None,
                        "tag_name": "v2.0.0",
                        "html_url": "https://github.com/openai/openai-python/releases/tag/v2.0.0",
                        "body": None,
                        "published_at": "2026-05-24T01:00:00Z",
                    }
                ],
            )
        return httpx.Response(404)

    client = httpx.Client(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    provider = GitHubReleasesProvider(client=client, max_repositories=1, max_releases_per_repo=1)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="OpenAI python SDK release",
        normalized_query="openai python sdk release",
        source_hint="github",
    )

    results = provider.search(query)

    assert seen_paths == ["/search/repositories", "/repos/openai/openai-python/releases"]
    assert [item.title for item in results] == ["openai/openai-python: v2.0.0"]


def test_github_activity_provider_returns_recent_issues_and_commits_for_repo_query() -> None:
    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path == "/repos/openai/openai-python/issues":
            return httpx.Response(
                200,
                json=[
                    {
                        "number": 123,
                        "title": "Add realtime agents support",
                        "html_url": "https://github.com/openai/openai-python/issues/123",
                        "body": "Proposal for realtime agent workflows.",
                        "state": "open",
                        "updated_at": "2026-05-25T01:00:00Z",
                    },
                    {
                        "number": 124,
                        "title": "Pull request should be ignored",
                        "pull_request": {"url": "https://api.github.com/pr/124"},
                    },
                ],
            )
        if request.url.path == "/repos/openai/openai-python/commits":
            return httpx.Response(
                200,
                json=[
                    {
                        "sha": "abc123",
                        "html_url": "https://github.com/openai/openai-python/commit/abc123",
                        "commit": {
                            "message": "Add agents streaming helpers\n\nExtended description.",
                            "author": {"date": "2026-05-25T02:00:00Z"},
                        },
                    }
                ],
            )
        return httpx.Response(404)

    client = httpx.Client(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    provider = GitHubActivityProvider(client=client, max_items_per_repo=2)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="Track openai/openai-python activity",
        normalized_query="track openai/openai-python activity",
        source_hint="github",
    )

    results = provider.search(query)

    assert seen_paths == ["/repos/openai/openai-python/issues", "/repos/openai/openai-python/commits"]
    assert len(results) == 2
    assert results[0].title == "openai/openai-python: issue #123 Add realtime agents support"
    assert results[0].source_name == "github-issues"
    assert results[0].raw == {
        "provider": "github_issues",
        "repo": "openai/openai-python",
        "number": 123,
        "state": "open",
        "updated_at": "2026-05-25T01:00:00Z",
    }
    assert results[1].title == "openai/openai-python: commit Add agents streaming helpers"
    assert results[1].source_name == "github-commits"
    assert results[1].raw == {
        "provider": "github_commits",
        "repo": "openai/openai-python",
        "sha": "abc123",
        "committed_at": "2026-05-25T02:00:00Z",
    }


def test_github_activity_provider_searches_repositories_when_no_repo_slug() -> None:
    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path == "/search/repositories":
            return httpx.Response(200, json={"items": [{"full_name": "langchain-ai/langchain"}]})
        if request.url.path == "/repos/langchain-ai/langchain/issues":
            return httpx.Response(200, json=[])
        if request.url.path == "/repos/langchain-ai/langchain/commits":
            return httpx.Response(
                200,
                json=[
                    {
                        "sha": "def456",
                        "html_url": "https://github.com/langchain-ai/langchain/commit/def456",
                        "commit": {
                            "message": "Refresh agent middleware",
                            "author": {"date": "2026-05-25T03:00:00Z"},
                        },
                    }
                ],
            )
        return httpx.Response(404)

    client = httpx.Client(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )
    provider = GitHubActivityProvider(client=client, max_repositories=1, max_items_per_repo=1)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="LangChain agent middleware",
        normalized_query="langchain agent middleware",
        source_hint="github_activity",
    )

    results = provider.search(query)

    assert seen_paths == [
        "/search/repositories",
        "/repos/langchain-ai/langchain/issues",
        "/repos/langchain-ai/langchain/commits",
    ]
    assert [item.title for item in results] == ["langchain-ai/langchain: commit Refresh agent middleware"]


def test_composite_source_provider_returns_results_from_each_provider() -> None:
    class StaticProvider:
        def __init__(self, source_name: str) -> None:
            self.source_name = source_name

        def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
            return [
                CheckerResult(
                    title=f"{self.source_name} for {query.query}",
                    source_name=self.source_name,
                )
            ]

    provider = CompositeSourceProvider([StaticProvider("one"), StaticProvider("two")])
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="open source agent",
        normalized_query="open source agent",
        source_hint="github",
    )

    results = provider.search(query)

    assert [item.source_name for item in results] == ["one", "two"]


def test_rss_feed_provider_returns_query_matching_rss_items() -> None:
    feed = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>AI News</title>
    <item>
      <title>OpenAI releases agent SDK update</title>
      <link>https://example.com/openai-sdk</link>
      <description>Agent workflow improvements shipped today.</description>
      <pubDate>Sun, 24 May 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Unrelated sports update</title>
      <link>https://example.com/sports</link>
      <description>No AI signal here.</description>
    </item>
  </channel>
</rss>
"""

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://feeds.example.com/ai.xml"
        return httpx.Response(200, text=feed)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = RssFeedProvider(["https://feeds.example.com/ai.xml"], client=client)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="OpenAI agent SDK",
        normalized_query="openai agent sdk",
        source_hint="news",
    )

    results = provider.search(query)

    assert len(results) == 1
    assert results[0].title == "OpenAI releases agent SDK update"
    assert results[0].source_name == "rss-feed"
    assert results[0].url == "https://example.com/openai-sdk"
    assert results[0].raw == {
        "provider": "rss_feed",
        "feed_url": "https://feeds.example.com/ai.xml",
        "published_at": "Sun, 24 May 2026 10:00:00 GMT",
    }


def test_rss_feed_provider_supports_atom_links() -> None:
    feed = """<?xml version="1.0" encoding="UTF-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Research</title>
  <entry>
    <title>Robotics policy draft published</title>
    <link href="https://example.com/robotics-policy" />
    <summary>New robotics regulation draft.</summary>
    <updated>2026-05-24T10:00:00Z</updated>
  </entry>
</feed>
"""

    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, text=feed)))
    provider = RssFeedProvider(["https://feeds.example.com/research.atom"], client=client)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="robotics regulation",
        normalized_query="robotics regulation",
        source_hint="news",
    )

    results = provider.search(query)

    assert [item.url for item in results] == ["https://example.com/robotics-policy"]


def test_arxiv_provider_returns_recent_papers() -> None:
    feed = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2605.12345v1</id>
    <updated>2026-05-25T10:00:00Z</updated>
    <published>2026-05-25T09:00:00Z</published>
    <title>Agentic Memory for Long-Horizon Research Workflows</title>
    <summary>
      We introduce a system for tracking weak technical signals over time.
    </summary>
    <author><name>Ada Researcher</name></author>
    <author><name>Ben Builder</name></author>
    <category term="cs.AI" />
    <category term="cs.CL" />
    <link href="http://arxiv.org/abs/2605.12345v1" rel="alternate" type="text/html" />
    <link title="pdf" href="http://arxiv.org/pdf/2605.12345v1" rel="related" type="application/pdf" />
  </entry>
</feed>
"""
    seen_params: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/query"
        seen_params.update(dict(request.url.params))
        return httpx.Response(200, text=feed)

    client = httpx.Client(
        base_url="https://export.arxiv.org",
        transport=httpx.MockTransport(handler),
    )
    provider = ArxivProvider(client=client, max_results=5)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="agentic memory research workflows",
        normalized_query="agentic memory research workflows",
        source_hint="research",
    )

    results = provider.search(query)

    assert seen_params == {
        "search_query": "all:agentic memory research workflows",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": "5",
    }
    assert len(results) == 1
    assert results[0].title == "Agentic Memory for Long-Horizon Research Workflows"
    assert results[0].url == "http://arxiv.org/pdf/2605.12345v1"
    assert results[0].source_name == "arxiv"
    assert results[0].raw == {
        "provider": "arxiv",
        "arxiv_id": "2605.12345v1",
        "published_at": "2026-05-25T09:00:00Z",
        "updated_at": "2026-05-25T10:00:00Z",
        "authors": ["Ada Researcher", "Ben Builder"],
        "categories": ["cs.AI", "cs.CL"],
    }


def test_hacker_news_provider_returns_search_hits() -> None:
    seen_params: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/search_by_date"
        seen_params.update(dict(request.url.params))
        return httpx.Response(
            200,
            json={
                "hits": [
                    {
                        "title": "Open source agents are spreading fast",
                        "url": "https://example.com/agents",
                        "story_text": "Developers discuss agent workflow adoption.",
                        "objectID": "123456",
                        "author": "example_user",
                        "points": 42,
                        "num_comments": 17,
                        "created_at": "2026-05-24T12:00:00Z",
                    },
                    {
                        "title": None,
                        "objectID": None,
                    },
                ]
            },
        )

    client = httpx.Client(
        base_url="https://hn.algolia.com",
        transport=httpx.MockTransport(handler),
    )
    provider = HackerNewsProvider(client=client, max_hits=5)
    query = TrackingQuery(
        intel_file_id=uuid4(),
        query="open source agents",
        normalized_query="open source agents",
        source_hint="hacker_news",
    )

    results = provider.search(query)

    assert seen_params == {
        "query": "open source agents",
        "tags": "story",
        "hitsPerPage": "5",
    }
    assert len(results) == 1
    assert results[0].title == "Open source agents are spreading fast"
    assert results[0].url == "https://example.com/agents"
    assert results[0].source_name == "hacker-news"
    assert results[0].raw == {
        "provider": "hacker_news",
        "object_id": "123456",
        "author": "example_user",
        "points": 42,
        "num_comments": 17,
        "created_at": "2026-05-24T12:00:00Z",
    }


def test_default_provider_registry_routes_search_to_hacker_news() -> None:
    registry = get_default_provider_registry()

    assert isinstance(registry.get("github"), CompositeSourceProvider)
    assert isinstance(registry.get("github_releases"), GitHubReleasesProvider)
    assert isinstance(registry.get("github_activity"), GitHubActivityProvider)
    assert isinstance(registry.get("github_issues"), GitHubActivityProvider)
    assert isinstance(registry.get("github_commits"), GitHubActivityProvider)
    assert isinstance(registry.get("research"), ArxivProvider)
    assert isinstance(registry.get("arxiv"), ArxivProvider)
    assert isinstance(registry.get("paper"), ArxivProvider)
    assert isinstance(registry.get("papers"), ArxivProvider)
    assert isinstance(registry.get("search"), HackerNewsProvider)
    assert isinstance(registry.get("hacker_news"), HackerNewsProvider)
    assert isinstance(registry.get("hn"), HackerNewsProvider)
    assert isinstance(registry.get("social"), HackerNewsProvider)
