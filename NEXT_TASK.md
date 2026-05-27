# NEXT_TASK.md

## Assignment

Owner action: deploy Render Blueprint and run hosted smoke test.

## Current Status

- `TASK-P4-05: Usage Limits and Cost Controls` is approved.
- P4 Commercialization slice is complete.
- `TASK-H1-01: Production Config and Security Baseline` is implemented and validated.
- `TASK-H1-02: Deployment Runbook and Release Checklist` is implemented and validated.
- `TASK-H1-03: Observability and Backup Baseline` is implemented and validated.
- `TASK-H1-04: Staging Readiness Review` is complete.
- `TASK-H2-01: Hosted Staging Target and Deployment Adapter` is implemented and validated.
- `TASK-H2-02: Staging Auth Guard` is implemented and validated.
- `TASK-H2-03: Hosted Staging Smoke Test Script` is implemented and validated.
- `TASK-H2-04: Hosted Staging Readiness Review` is complete.
- `TASK-H3-01: Workspace Membership Guard` is implemented and validated.
- `TASK-H3-02: Workspace Member Management` is implemented and validated.
- `TASK-H3-03: Staging User Access Token` is implemented and validated.
- `TASK-H3-04: Access Control Readiness Review` is complete.
- `TASK-H4-01: Admin Audit Log` is implemented and validated.
- `TASK-H4-02: Audit Log Export` is implemented and validated.
- `TASK-H4-03: Security Response Headers` is implemented and validated.
- `TASK-H4-04: Environment Readiness Check` is implemented and validated.
- `TASK-H4-05: Admin Rate Limit` is implemented and validated.
- `TASK-H4-06: Runtime Readiness Endpoint` is implemented and validated.
- `TASK-H4-07: Production Env Template` is implemented and validated.
- `TASK-H4-08: Predeploy Checklist Script` is implemented and validated.
- H5 gap closure is implemented and validated:
  - GitHub Releases source provider added as the first real provider.
  - Celery Beat now schedules source checks, lifecycle dormancy/resurrection, and notification delivery.
  - Homepage scaffold replaced with a working dashboard.
  - REVIEW status updated.
  - Stale temporary SQLite artifact removed.
- H6 workspace isolation hardening is implemented and validated:
  - Commercial routes now enforce workspace access and scope service queries.
  - Source check runs now persist `workspace_id` via migration `0014_source_check_run_workspace`.
  - Report exports use authenticated frontend downloads.
  - Backend report dependency `reportlab` is recorded for reproducible installs.
- H7 Hacker News source pack is implemented and validated:
  - `search`, `hacker_news`, `hn`, and `social` source hints route to HN Search.
  - HN provider uses public no-key search endpoints and stores source metadata for match suggestions.
- H8 source operations suggestion triage is implemented and validated:
  - Sources page can generate match suggestions from source-check runs.
  - Fresh source-check runs automatically attempt suggestion generation.
  - Suggested evidence links back to the relevant Intel File for acceptance/review.
- H9 Intel Files saved views is implemented and validated:
  - Analysts can save, apply, and delete local Intel File filter/sort/page-size views.
  - Saved views persist in browser localStorage for recurring triage workflows.
- H10 Sources inline suggestion actions is implemented and validated:
  - Sources suggested evidence can be accepted inline, creating raw item and evidence records.
  - Suggestions can be dismissed inline without leaving the source operations page.
  - Match suggestion status updates are available through the v1 API.
- H11 GitHub activity source pack is implemented and validated:
  - GitHub source checks now combine releases, recent issues, and recent commits.
  - `github_activity`, `github_issues`, and `github_commits` source hints are available.
  - Provider limits are configurable without requiring a GitHub token.
- H12 arXiv research source pack is implemented and validated:
  - `research`, `arxiv`, `paper`, and `papers` source hints route to arXiv Atom API.
  - Research signal tracking queries now use the `research` source hint.
  - arXiv provider limits and timeout are configurable without credentials.
- H13 source provider health visibility is implemented and validated:
  - Source provider health API summarizes enabled queries, recent results, last result time, latest run status, and latest run error by source hint.
  - Sources page shows provider health and last-error visibility for source operations.
- H14 workspace-backed shared saved views is implemented and validated:
  - Intel File saved views are persisted by workspace through `0015_intel_file_saved_views`.
  - Analysts can save, apply, and delete shared Intel File views from the workbench.
  - Saved views are scoped by workspace and no longer depend on browser localStorage.
- H15 provider-specific error attribution is implemented and validated:
  - Source provider health now attributes recent failures back to each failed query's `source_hint`.
  - Sources page shows recent error counts and latest provider-level error by hint.
- H16 shared saved view mutation states is implemented and validated:
  - Intel Files saved view loading, saving, and deleting now have explicit UI states.
  - Saved view controls are disabled during mutations to prevent duplicate submissions.
- H17 provider health failed-query drill-down is implemented and validated:
  - Provider health API now returns recent failed tracking queries per source hint.
  - Sources page exposes failed query/error details through expandable provider health rows.
- H18 provider health filtering is implemented and validated:
  - Sources page can filter provider health by all, erroring, active, and active-with-no-results source hints.
  - Provider hint metrics now show visible versus total provider health rows.
- H19 saved view rename/update affordances are implemented and validated:
  - Saved views can be patched by id through the v1 API without relying on name-based upsert.
  - Intel Files workbench can rename and update the selected shared view with current filters.
- H20 saved-view default workflow is implemented and validated:
  - Saved views can be marked as the workspace default while preserving one default per workspace.
  - Intel Files workbench automatically applies the default shared view on load.
- H21 saved-view usage metadata is implemented and validated:
  - Saved views now support descriptions and last-used timestamps via migration `0017_saved_view_usage_metadata`.
  - Intel Files workbench records last-used time when a shared view is applied and shows owner/description usage context.
- H22 PyPI package source pack is implemented and validated:
  - `package`, `pypi`, `python_package`, and `sdk` source hints now check public PyPI package metadata without credentials.
  - PyPI provider settings are documented in development and production env templates.
- H23 package signal tracking-query routing is implemented and validated:
  - Intel files mentioning Python package/SDK signals now generate a `pypi` tracking query automatically.
  - PyPI provider can now be reached by normal tracking-query generation, not only by manually edited source hints.
- H24 hiring source hint coverage is implemented and validated:
  - `careers`, `hiring`, and `jobs` source hints now route to the no-key Hacker News provider instead of no-oping.
  - Hiring-signal tracking queries generated by the core workflow now have a provider path in staging.
- H25 news source hint fallback coverage is implemented and validated:
  - `news` now combines configured RSS feeds with no-key Hacker News fallback coverage.
  - `funding`, `market`, and `policy` source hints now have provider paths even before RSS feeds are configured.
- H26 specific news-adjacent tracking hints are implemented and validated:
  - Funding, market, and policy intel files now generate `funding`, `market`, and `policy` tracking hints instead of collapsing into generic `news`.
  - Provider health can now attribute these signal classes separately while still using the H25 fallback provider path.
- H27 source-check query rotation is implemented and validated:
  - Tracking queries now record `last_checked_at` through migration `0018_tracking_query_last_checked`.
  - Source checks prioritize never-checked and oldest-checked queries so later queries are not starved by the oldest created rows.
- H28 provider health check-rotation visibility is implemented and validated:
  - Provider health now exposes `never_checked_count` and `last_checked_at` by source hint.
  - Sources page shows never-checked backlog and last checked time for each provider hint.
- H29 Intel File tracking-query visibility is implemented and validated:
  - Intel File detail now lists generated tracking queries with source hint, enabled state, rationale, and last checked time.
  - A read-only tracking-query list API is available at `GET /api/v1/intel-files/{intel_file_id}/tracking-queries`.
  - Analysts can generate or regenerate tracking queries from the Intel File detail page.
- H30 Intel File tracking-query controls are implemented and validated:
  - Tracking queries can be enabled or paused through `PATCH /api/v1/intel-files/{intel_file_id}/tracking-queries/{tracking_query_id}`.
  - Intel File detail now exposes pause/enable actions so noisy queries can be removed from source-check rotation without regeneration.
  - Active and never-checked tracking counts now reflect enabled queries only.
- H31 Intel File suggestion dismiss workflow is implemented and validated:
  - Intel File detail now supports dismissing open match suggestions without switching to the Sources page.
  - Dismissed suggestions are removed from the open review list immediately after the API confirms the status update.

## Goal

Create the real hosted staging deployment using the prepared Render Blueprint, access-control baseline, audit log/export, security headers, readiness endpoint, rate limit, env preflight, predeploy script, real GitHub Releases provider, and scheduled worker loop.

## Validation

- Push repository to GitHub.
- Push repository to GitLab.
- Create Render Blueprint from `render.yaml`.
- Fill manual secrets and hosted URLs.
- Create `.env.production` from `.env.production.example`.
- Run `scripts\predeploy-check.ps1`.
- Run `scripts\check-env-readiness.ps1` against the production-like env file.
- Run migrations through `0018_tracking_query_last_checked`.
- Run `scripts\smoke-staging.ps1` against hosted URLs with `-AdminApiKey`.

## Next Implementation Candidates After Staging

- Add per-user saved view preferences after real hosted auth is selected.
- Add additional no-key source packs only after observed staging usage shows a clear gap.
