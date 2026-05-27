# REVIEW.md

Review findings, risks, and approval notes for Signal Tracker.

## Current Review Status

P0 planning review completed on 2026-05-23.
P1-P4 and H1-H4 implementation completed and re-reviewed on 2026-05-24.
H5 hardening gap closure completed on 2026-05-24.
H6 workspace isolation hardening completed on 2026-05-24.
H7 Hacker News source pack completed on 2026-05-24.
H8 source operations suggestion triage completed on 2026-05-25.
H9 Intel Files saved views completed on 2026-05-25.
H10 Sources inline suggestion actions completed on 2026-05-26.
H11 GitHub activity source pack completed on 2026-05-26.
H12 arXiv research source pack completed on 2026-05-26.
H13 source provider health visibility completed on 2026-05-26.
H14 workspace-backed shared saved views completed on 2026-05-27.
H15 provider-specific error attribution completed on 2026-05-27.
H16 shared saved view mutation states completed on 2026-05-27.
H17 provider health failed-query drill-down completed on 2026-05-27.

## Verdict

`APPROVE_FOR_HOSTED_STAGING_WITH_WORKSPACE_ISOLATION`

The repository is ready for hosted staging deployment, with workspace-scoped commercial routes, reproducible report dependencies, GitHub Releases/Issues/Commits, RSS, Hacker News, and arXiv source providers, plus known follow-ups for richer commercial UI depth.

## 2026-05-27 H17 Provider Health Failed-Query Drill-Down Review

### Verdict

`APPROVE`

### Scope Reviewed

- Provider health responses now include recent failed tracking queries with query text and error message.
- Failed-query details are capped per provider hint to keep the health response compact.
- Sources page exposes provider failure details through expandable rows in the Provider Health table.
- Backend tests cover failed-query drill-down data.

### Findings

No blocking findings.

### Verified

- Focused source check tests: passed.
- Frontend type-check: passed.

### Residual Risks

- Provider health filtering by errored/active hints remains a UI polish follow-up.

## 2026-05-27 H16 Shared Saved View Mutation States Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added loading state while workspace saved views are fetched.
- Added saving and deleting states for shared saved view mutations.
- Disabled saved view controls during active mutations to prevent duplicate submissions.
- Updated button labels for in-progress save/delete operations.

### Findings

No blocking findings.

### Verified

- Frontend type-check: passed.
- Frontend production build: passed.

### Residual Risks

- Saved views still use name-based upsert. A later UI pass can add explicit rename/update behavior.

## 2026-05-27 H15 Provider-Specific Error Attribution Review

### Verdict

`APPROVE`

### Scope Reviewed

- Source provider health now parses failed source-check query ids from run errors.
- Failed queries are mapped back to their `source_hint`.
- Provider health responses include `recent_error_count` and `latest_error`.
- Sources page shows recent provider errors and latest provider-level error by hint.
- Added backend coverage for provider-specific error attribution.

### Findings

No blocking findings.

### Verified

- Focused source check tests: passed.
- Frontend type-check: passed.

### Residual Risks

- Failed-query drill-down is now available in provider health. Filtering remains a future UI polish item.

## 2026-05-27 H14 Workspace-Backed Shared Saved Views Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added `0015_intel_file_saved_views` migration and ORM model.
- Added workspace-scoped saved view schemas, service, and API routes.
- Added `GET/POST/DELETE /api/v1/intel-file-saved-views`.
- Intel Files page now loads, saves, applies, and deletes saved views through the backend API instead of localStorage.
- Added backend tests for create/list/delete, upsert by workspace slug, and workspace isolation.

### Findings

No blocking findings.

### Verified

- Focused saved view tests: passed.
- Frontend type-check: passed.

### Residual Risks

- Saved view mutation loading states are now implemented. Rename/update affordances remain a future polish item.

## 2026-05-26 H13 Source Provider Health Visibility Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added source provider health summaries by source hint.
- Added `GET /api/v1/source-checks/provider-health`.
- Sources page now shows enabled query count, recent result count, last result time, latest run status, and latest run error.
- Added backend API coverage for provider health summaries.

### Findings

No blocking findings.

### Verified

- Focused source check tests: passed.
- Frontend type-check: passed.

### Residual Risks

- Provider-specific errors are now summarized by source hint; individual failed-query drill-down remains a future improvement.

## 2026-05-26 H12 arXiv Research Source Pack Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added an arXiv Atom API provider for research/paper signals.
- Registered `research`, `arxiv`, `paper`, and `papers` source hints.
- Routed `SignalType.RESEARCH` tracking queries to the `research` source hint.
- Added configurable arXiv max-result and timeout settings to environment templates.
- Added deterministic provider and tracking-query tests using mocked Atom responses.

### Findings

No blocking findings.

### Verified

- Focused source check and tracking query tests: passed.

### Residual Risks

- arXiv API usage should stay conservative; production should monitor provider latency and failures.
- Failed source-check errors still need provider-specific attribution for faster triage.

## 2026-05-26 H11 GitHub Activity Source Pack Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added a GitHub activity provider for recent issues and commits.
- Upgraded the default `github` source hint to combine releases, issues, and commits.
- Added explicit `github_activity`, `github_issues`, and `github_commits` source hints.
- Added configurable GitHub activity item limits to environment templates.
- Added deterministic provider tests using mocked GitHub API responses.

### Findings

No blocking findings.

### Verified

- Focused source check tests: passed.

### Residual Risks

- Unauthenticated GitHub API usage is rate-limited; production should set `GITHUB_API_TOKEN` if source-check volume increases.
- Broader research coverage beyond arXiv, such as patents or conference feeds, remains a future provider-pack follow-up.

## 2026-05-26 H10 Sources Inline Suggestion Actions Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added v1 API support for match suggestion status updates.
- Added backend tests for dismissing suggestions and missing suggestion handling.
- Sources page can accept suggested evidence inline through the existing accept workflow.
- Sources page can dismiss suggested evidence inline without navigating to an Intel File detail page.

### Findings

No blocking findings.

### Verified

- Focused match suggestion tests: passed.
- Backend pytest: passed.
- Frontend type-check and build: passed.

### Residual Risks

- Suggestions are still generated from completed source-check runs only; richer provider packs are the next source coverage improvement.

## 2026-05-25 H9 Intel Files Saved Views Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added browser-local saved views to the Intel Files workbench.
- Saved views capture query, lifecycle status, sort, order, and page size.
- Analysts can apply and delete saved views without a backend migration.

### Findings

No blocking findings.

### Verified

- Frontend type-check and build: passed.

### Residual Risks

- Saved views are browser-local. Team-shared saved views should become a workspace-backed feature later.

## 2026-05-25 H8 Source Operations Suggestion Triage Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added frontend API client for source-check match suggestion generation.
- Sources page can generate suggestions from run history and automatically after a fresh run.
- Sources page displays generated suggestions with confidence, source, status, and Intel File navigation.
- Invalid source-check run suggestion generation now returns API 404 instead of surfacing as an unhandled server error.

### Findings

No blocking findings.

### Verified

- Focused match suggestion tests: passed.
- Frontend type-check and build: passed.

### Residual Risks

- Suggested evidence acceptance still happens from the Intel File detail page; a future workflow can add inline accept/dismiss actions on the Sources page.

## 2026-05-24 H7 Hacker News Source Pack Review

### Verdict

`APPROVE`

### Scope Reviewed

- Added no-credential Hacker News provider using HN Search by Algolia.
- Routed `search`, `hacker_news`, `hn`, and `social` source hints to Hacker News.
- Added provider tuning env vars for max hits, timeout, and tags.
- Added deterministic provider and registry tests.

### Findings

No blocking findings.

### Verified

- Focused source check tests: passed.

### Residual Risks

- HN Search is public and no-key, so production should keep conservative query limits and monitor provider failures.
- Broader non-HN source coverage still depends on configured RSS feeds and future provider packs.

## 2026-05-24 H6 Workspace Isolation Hardening Review

### Verdict

`APPROVE`

### Scope Reviewed

- Workspace-scoped briefing and report exports.
- Workspace-scoped alerts, source check runs, match suggestions, lifecycle operations, scoring, tracking query generation, extraction, and trend archives.
- Source check run ownership persisted via `0014_source_check_run_workspace`.
- Frontend report export switched from unauthenticated links to header-bearing downloads.
- Reproducible backend dependency set includes `reportlab`.

### Findings

No blocking findings.

### Verified

- Backend pytest: 145 passed.
- Frontend type-check: passed.
- Frontend production build: passed.
- Alembic upgrade through `0014_source_check_run_workspace`: passed on SQLite migration smoke test.

### Residual Risks

- Hosted Render deployment is still not executed in the real account environment.
- Embedded Celery Beat is acceptable for one worker, but should be split or locked before horizontal worker scaling.
- Additional source packs are still needed for broad AI opportunity tracking.

## 2026-05-24 H5 Hardening Gap Closure Review

### Verdict

`APPROVE`

### Scope Reviewed

- Backend regression test baseline.
- GitHub Releases source provider.
- Celery Beat schedule for source checks, lifecycle dormancy/resurrection, and notification delivery.
- Dashboard replacement for the previous scaffold homepage.
- Environment templates and worker startup commands.
- Temporary SQLite artifact cleanup.

### Findings

No blocking findings.

### Verified

- Backend pytest: 137 passed.
- Frontend type-check: passed.
- Frontend production build: passed.
- Celery app loads beat schedule keys: `source-checks-run-due`, `lifecycle-dormancy-run`, `notification-delivery-run`.
- Removed stale `backend/tmp_p1_02_rereview.db`.

### Residual Risks

- Hosted Render deployment is still not executed in the real account environment.
- GitHub Releases is the first real provider; more source packs are still needed for broad AI opportunity tracking.
- Frontend is now demoable as a dashboard, but deeper commercial workflows still need richer filtering, saved views, and source operations UI.

## Findings

### Historical P1 — Missing OpenSpec change packages after P1-02

The OpenSpec execution layer currently has change packages for:

- `p1-01-repo-scaffold`
- `p1-02-core-domain-model`

Resolved. Later P1-P4 and H1-H4 task packages were created during execution.

### Historical P2 — Default stack should be confirmed by the implementation AI

Resolved. The implemented stack is FastAPI + Next.js + PostgreSQL + Redis + Celery.

### Historical P2 — Commercial requirements are intentionally not in MVP acceptance

Resolved. Commercial capabilities were implemented after MVP slices in P4.

## Open Questions

- Which source pack should follow GitHub Releases/RSS/Hacker News: GitHub Issues/Commits, arXiv, or curated company blogs?
- Should hosted staging run with embedded Celery Beat on the worker service, or split Beat into a separate Render worker after traffic increases?
- Which commercial workflow deserves the next UI pass: source operations, saved views, or team review queues?

## Review Checklist

### Product

- [x] MVP proves lifecycle loop.
- [x] Out-of-scope items are explicit.
- [x] First niche is clear.
- [x] User scenarios are testable.

### Architecture

- [x] `IntelFile` remains primary object.
- [x] Raw item and evidence are separated.
- [x] Lifecycle transitions are auditable.
- [x] Scoring is explainable.
- [x] Source taxonomy supports early discovery and verification.

### AI Development OS

- [x] Tasks have owner skill and acceptance criteria.
- [x] ADRs cover major decisions.
- [x] Skill boundaries are clear.
- [x] Definition of Done requires validation and review.

### Implementation Readiness

- [x] P1 tasks can be assigned without inventing scope.
- [x] Data model is specific enough for migrations.
- [x] API areas are clear enough for route planning.
- [x] Test strategy is clear enough to begin.

## P1A Scaffold Review (Pending)

Implementation agent completed TASK-P1-01 on 2026-05-23.

### Verified by implementation agent

- Backend pytest: 1 passed (`test_health_returns_ok`)
- Frontend type-check: pass
- Frontend build: pass (9 static routes)
- Worker import: `workers.tasks.ping` registered
- Alembic: empty initial migration `0001_scaffold` present

### Scope check

- No IntelFile, lifecycle, scoring, alerts, briefing, auth, or crawler code detected.
- Frontend pages are placeholders only.

### Follow-ups

- P1: Run full P1A gate review with docker compose + health curl (Codex/Review Skill).
- P2: Next.js workspace root warning mitigated via `outputFileTracingRoot`.

## Approved Next Step

Start:

- Task card: `docs/task-cards/TASK-P1-01-repo-implementation-scaffold.md`
- Change package: `openspec/changes/p1-01-repo-scaffold/`
- Prompt: `prompts/p1-scaffold-agent.md`

## Review Notes

The planning package has the right shape for AI-assisted delivery:

```text
Strategy docs
  -> Methodology docs
  -> Architecture docs
  -> Task cards
  -> OpenSpec changes
  -> Review gates
```

The main risk is not missing planning; it is scope creep during implementation. Keep P1 focused on the lifecycle loop and reject generic news-dashboard work.

---

## TASK-P1-02 Review — 2026-05-23

### Verdict

`REQUEST_CHANGES`

The core tables, relationships, migration, schemas, and sample-chain tests are present, and backend tests pass. However, two data-contract issues should be fixed before starting `TASK-P1-03`, because they will otherwise leak into intake/extraction behavior.

### Findings

#### P1 — URL-only submissions cannot be stored as planned

`RawItem.content` is non-nullable in both ORM and migration, but the Inbox/API specs explicitly allow URL-only submission where body text may be missing. This will make `TASK-P1-03` either fail on URL-only intake or force it to invent placeholder content. Fix by allowing nullable content, defaulting to an empty string deliberately, or adding a separate extraction status/body availability field and updating specs accordingly.

Files:

- `backend/app/models/raw_item.py`
- `backend/alembic/versions/0002_core_domain.py`

#### P1 — SignalAnalysis cannot persist the extraction contract fields

`SignalAnalysis` stores summary/type/entities/keywords/claims and three score hints, but the agreed AI extraction contract also includes `suggested_tracking_queries`, `risk_hint`, `opportunity_types`, and `rationale`. Without columns or a structured JSON payload for these, `TASK-P1-04` will either discard useful extraction output or overload `raw_output` for fields the rest of the app needs to query/display.

Files:

- `backend/app/models/signal_analysis.py`
- `backend/app/schemas/domain.py`
- `docs/specs/ai-extraction-contract.md`

#### P2 — Enum values are not database-constrained

The ORM uses SQLAlchemy `Enum(..., native_enum=False)` but the migration creates plain string columns without check constraints. This means invalid lifecycle/status/type strings can be inserted at the database level and only fail later when the ORM reads them. This is not blocking the current sample tests, but lifecycle/status correctness is central to the product, so add DB-level check constraints or explicit validation before P1 lifecycle work.

Files:

- `backend/app/models/intel_file.py`
- `backend/app/models/enums.py`
- `backend/alembic/versions/0002_core_domain.py`

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_models.py -q
# 6 passed

python -m pytest tests/ -q
# 7 passed
```

Passed migration smoke with temporary SQLite database:

```powershell
$env:DATABASE_URL='sqlite:///./tmp_p1_02_review.db'
python -m alembic upgrade head
```

### Required Before Next Task

- Fix `RawItem.content` vs URL-only intake contract.
- Add persistent fields or structured first-class storage for the missing extraction contract fields.
- Add tests covering URL-only raw item storage and extraction-contract persistence.

### Follow-Up

- Consider enum DB constraints before lifecycle/status mutation work.

---

## TASK-P1-02 Re-Review — 2026-05-23

### Verdict

`REQUEST_CHANGES`

The prior model/schema findings are fixed, and tests pass. The remaining blocker is migration compatibility: the new `0003_intake_extraction_fields` migration fails in the SQLite migration smoke used by the project review flow.

### Findings

#### P1 — `0003_intake_extraction_fields` migration fails on SQLite

The migration uses `op.alter_column("raw_items", "content", nullable=True)`, which emits `ALTER TABLE raw_items ALTER COLUMN content DROP NOT NULL`. SQLite does not support that syntax, so `alembic upgrade head` fails before reaching a valid head state. Since current tests and review smoke use SQLite for fast local validation, the migration must use Alembic batch mode or another SQLite-compatible approach.

Files:

- `backend/alembic/versions/0003_intake_extraction_fields.py`

### Resolved In This Re-Review

- `RawItem.content` ORM/schema now supports URL-only intake.
- `SignalAnalysis` ORM/schema now stores `suggested_tracking_queries`, `opportunity_types`, `risk_hint`, and `rationale`.
- Tests now cover URL-only raw items and extraction-contract persistence.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_models.py -q
# 8 passed

python -m pytest tests/ -q
# 9 passed
```

Failed:

```powershell
$env:DATABASE_URL='sqlite:///./tmp_p1_02_rereview.db'
python -m alembic upgrade head
```

Failure:

```text
sqlite3.OperationalError: near "ALTER": syntax error
ALTER TABLE raw_items ALTER COLUMN content DROP NOT NULL
```

### Required Before Next Task

- Update `0003_intake_extraction_fields.py` to be SQLite-compatible, likely with `op.batch_alter_table("raw_items")` for the nullable change.
- Re-run `python -m alembic upgrade head` against a temporary SQLite database.

---

## TASK-P1-02 Final Re-Review — 2026-05-23

### Verdict

`APPROVE`

The remaining migration blocker is fixed. `0003_intake_extraction_fields` now uses Alembic batch mode for the nullable change and migrates successfully in the SQLite smoke path. The previous model/schema issues remain resolved.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_models.py -q
# 8 passed

python -m pytest tests/ -q
# 9 passed

$env:DATABASE_URL='sqlite:///./tmp_p1_02_final_review.db'
python -m alembic upgrade head
# upgraded through 0003_intake_extraction_fields
```

### Approved Next Step

Start `TASK-P1-03: Manual signal submission`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-03-manual-signal-submission/
  proposal.md
  design.md
  tasks.md
```

Use:

- `docs/task-cards/TASK-P1-03-manual-signal-submission.md`
- `openspec/specs/inbox/spec.md`
- `docs/specs/api-contracts.md`
- `docs/specs/ui-spec.md`

---

## TASK-P1-03 Review — 2026-05-23

### Verdict

`REQUEST_CHANGES`

The core manual intake flow is implemented and validation passes, but the user-facing error path does not yet meet the task acceptance criterion that error messages are readable.

### Findings

#### P1 — Empty or invalid submissions show a generic frontend error instead of a readable message

The form allows submitting all three fields empty. The backend correctly rejects this via Pydantic validation with HTTP 422, but the frontend API helper throws `Request failed: 422` for any non-400 error. That means users see a generic transport error instead of the domain message "At least one of url, title, or content is required." The task explicitly requires readable errors, so either add client-side validation before submit or normalize 422 validation errors into the shared API error shape and parse them in the client.

Files:

- `apps/web/src/components/inbox/SubmissionForm.tsx`
- `apps/web/src/lib/api.ts`
- `backend/app/schemas/inbox.py`

#### P2 — API error envelope is inconsistent for validation/service errors

The contract says API responses use `{ success, data, error }`, but `HTTPException(detail=ApiResponse(...))` returns the envelope under `detail`, and FastAPI validation errors return the default 422 shape. This does not block the happy path, but it will make frontend error handling brittle as soon as source selection or validation expands.

Files:

- `backend/app/api/v1/inbox.py`
- `backend/app/schemas/api.py`

### Passed Scope Checks

- `POST /api/v1/inbox/submit` exists.
- `GET /api/v1/inbox` exists.
- Manual source fallback is implemented.
- Duplicate submissions return the existing item with `duplicate: true`.
- URL-only submission is covered.
- Inbox UI has submission form and pending-analysis list.
- No extraction, IntelFile, lifecycle, scoring, alerts, or briefing logic was added.
- OpenSpec change package exists for `p1-03-manual-signal-submission`.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_inbox.py -q
# 6 passed

python -m pytest tests/ -q
# 15 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Required Before Next Task

- Make empty/invalid submission errors readable in the UI.
- Add or update a test covering the chosen error behavior.
- Re-run backend tests and frontend type-check/build.

---

## TASK-P1-03 Re-Review — 2026-05-23

### Verdict

`APPROVE`

The readable-error finding is resolved. The Inbox form now validates empty submissions client-side with a clear message, and the API helper can normalize backend 400/422 validation responses into readable errors. Backend tests cover empty and whitespace-only validation.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_inbox.py -q
# 7 passed

python -m pytest tests/ -q
# 16 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Approved Next Step

Start `TASK-P1-04: AI extraction prompt and mock fallback`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-04-ai-extraction/
  proposal.md
  design.md
  tasks.md
```

Use:

- `docs/task-cards/TASK-P1-04-ai-extraction.md`
- `openspec/specs/extraction/spec.md`
- `docs/specs/ai-extraction-contract.md`
- `backend/app/models/signal_analysis.py`
- `backend/app/schemas/domain.py`

---

## TASK-P1-04 Review — 2026-05-23

### Verdict

`REQUEST_CHANGES`

The extraction prompt, mock fallback, API route, persistence flow, and optional Inbox analyze action are mostly in place. Existing tests and frontend validation pass. One service-level guard is too broad and will break the next phase once any IntelFile exists.

### Findings

#### P1 — Extraction fails whenever any IntelFile already exists

`analyze_raw_item` commits a new `SignalAnalysis`, then counts the entire `intel_files` table and raises `RuntimeError("Extraction must not create intel files.")` if the count is greater than zero. This does not prove the extraction just created a file; it rejects analysis in any database that already has an unrelated IntelFile. After `TASK-P1-05` creates the first file, later raw-item analysis will start failing.

Fix by removing this global table-count guard, or by comparing before/after counts inside a test-only assertion if you still want that safety check. Keep the acceptance covered with a test that analysis does not create an IntelFile for the analyzed raw item.

File:

- `backend/app/modules/extraction/service.py`

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_extraction.py -q
# 6 passed

python -m pytest tests/ -q
# 22 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

Failed smoke:

```text
Existing IntelFile + new RawItem analysis -> RuntimeError: Extraction must not create intel files.
```

### Required Before Next Task

- Remove or narrow the global `IntelFile` count guard.
- Add a regression test where an unrelated IntelFile already exists and analyzing a new RawItem still succeeds.
- Re-run backend tests and frontend type-check/build.

---

## TASK-P1-04 Re-Review — 2026-05-23

### Verdict

`APPROVE`

The blocker is fixed. Extraction no longer checks the global `IntelFile` table during analysis, so it remains responsible only for creating or reusing `SignalAnalysis`. A regression test now covers the case where an unrelated IntelFile already exists and analysis of a new RawItem still succeeds without changing the IntelFile count.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_extraction.py -q
# 7 passed

python -m pytest tests/ -q
# 23 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Approved Next Step

Start `TASK-P1-05: IntelFile creation from analyzed signals`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-05-intel-file-creation/
  proposal.md
  design.md
  tasks.md
```

---

## TASK-P1-05 Review — 2026-05-23

### Verdict

`APPROVE`

Intel file creation is implemented within scope. The backend can promote an analyzed RawItem into an IntelFile, creates first-seen Evidence and a created IntelEvent, prevents duplicate promotion idempotently, and refuses unanalyzed RawItems with a readable error. The Inbox create action, Intel Files list, and detail skeleton are wired.

### Findings

No blocking findings.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_intel_files.py -q
# 6 passed

python -m pytest tests/ -q
# 29 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Duplicate promotion is handled at service level for the current single-user MVP flow. Add database-level protection or transaction hardening before concurrent/background promotion paths are introduced.

### Approved Next Step

Start `TASK-P1-06: Evidence Timeline`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-06-evidence-timeline/
  proposal.md
  design.md
  tasks.md
```

---

## TASK-P1-06 Review — 2026-05-23

### Verdict

`APPROVE`

Evidence timeline is implemented within scope. The backend can attach a RawItem to an IntelFile as follow-up evidence, rejects duplicate attachments, updates evidence/source counts and last_seen_at, creates an evidence_added IntelEvent, and returns an ordered timeline. The Intel File detail UI now has a minimal manual attach form and refreshes after attachment.

### Findings

No blocking findings.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_evidence_timeline.py -q
# 6 passed

python -m pytest tests/ -q
# 35 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Evidence duplicate protection is fine for the MVP request path. Before adding automated/background attachment, catch database uniqueness races and consider recalculating evidence_count from the table instead of incrementing.
- Consider constraining confidence to the intended 0.0-1.0 range in a later hardening pass.

### Approved Next Step

Start `TASK-P1-07: Lifecycle Evaluation V1`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-07-lifecycle-evaluation/
  proposal.md
  design.md
  tasks.md
```

---

## TASK-P1-07 Review — 2026-05-23

### Verdict

`APPROVE`

Lifecycle evaluation v1 is implemented within scope. The backend exposes `POST /api/v1/intel-files/{id}/evaluate`, applies deterministic lifecycle rules, persists a `LifecycleSnapshot` for every evaluation, creates a `status_changed` IntelEvent when status changes, and honors the configurable dormancy threshold. Tests cover the required states and transition paths.

### Findings

No blocking findings.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_lifecycle.py -q
# 12 passed

python -m pytest tests/ -q
# 47 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- `score_changes` currently reports before/after values as identical because scoring recalculation is intentionally deferred to `TASK-P1-08`.
- Lifecycle rule thresholds are deliberately simple. Revisit priority ordering after scoring v1 and alerts are implemented.

### Approved Next Step

Start `TASK-P1-08: Scoring Engine V1`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-08-scoring-engine/
  proposal.md
  design.md
  tasks.md
```

---

## TASK-P1-08 Review — 2026-05-23

### Verdict

`APPROVE`

Scoring engine v1 is implemented within scope. The backend exposes `POST /api/v1/intel-files/{id}/score`, calculates deterministic explainable scores, clamps values to 0-10, updates current IntelFile scores used by later alerts, stores a score snapshot with rationale/inputs, and creates a `score_changed` event when persisted scores change. Scoring does not mutate lifecycle status.

### Findings

No blocking findings.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_scoring.py -q
# 8 passed

python -m pytest tests/ -q
# 55 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- `novelty_score` is calculated and persisted inside snapshot rationale/metadata, but there is no first-class `IntelFile.novelty_score` column. This is acceptable for P1-08, but revisit the data model if novelty needs fast list filtering or historical diffs.
- Score formulas are intentionally simple. Tune weights after alerts and briefing make score impact more visible.

### Approved Next Step

Start `TASK-P1-09: Alerts V1`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-09-alerts-v1/
  proposal.md
  design.md
  tasks.md
```

---

## TASK-P1-09 Review — 2026-05-23

### Verdict

`APPROVE`

Alerts v1 is implemented within scope. Lifecycle and scoring services create deduplicated in-app alerts for resurrection, verification/debunk, and score threshold crossings. Alerts can be listed, acknowledged, and dismissed from the UI. No external notification channels were added.

### Findings

No blocking findings.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_alerts.py -q
# 5 passed

python -m pytest tests/ -q
# 60 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Alert dedupe keys are embedded in the message field. This is acceptable for MVP, but a dedicated dedupe_key column would be cleaner before multi-channel delivery.

### Approved Next Step

Start `TASK-P1-10: Daily Briefing V1`.

Before implementation, create the matching OpenSpec change package:

```text
openspec/changes/p1-10-daily-briefing/
  proposal.md
  design.md
  tasks.md
```

---

## TASK-P1-10 Review — 2026-05-23

### Verdict

`APPROVE`

Daily briefing v1 is implemented within scope. The API returns a configurable-window briefing with new files, updated files, resurrected signals, high-opportunity files, and risk/noise candidates. Items include IDs, title, status, scores, reason, and key evidence. The frontend Briefing page renders all sections with empty states.

### Findings

No blocking findings.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_briefings.py -q
# 6 passed

python -m pytest tests/ -q
# 66 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Briefing is generated live from current DB state. Persisted/generated briefing artifacts can wait until report builder or scheduled delivery.

### Approved Next Step

Start `TASK-P1-11: MVP Acceptance Tests`.

---

## TASK-P1-11 Review — 2026-05-23

### Verdict

`APPROVE`

The MVP acceptance test now verifies the full lifecycle loop:

```text
manual intake -> extraction -> intel file -> scoring -> dormant fixture -> follow-up evidence -> resurrection -> alert -> briefing
```

The end-to-end backend acceptance test passes, backend full suite passes, and frontend type-check/build pass.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_mvp_acceptance.py -q
# 1 passed

python -m pytest tests/ -q
# 67 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Remaining Risks

- No authentication or multi-user isolation yet.
- No production migrations smoke was run in this review pass.
- Matching is manual; automated matching remains P2.
- Briefings are generated live and not persisted.
- Alert dedupe still uses encoded message keys rather than a dedicated column.

### P1 Verdict

`APPROVE`

P1 MVP foundation is complete enough to demo and continue into P2 tracking/source automation work.

---

## TASK-P2-01 Review — 2026-05-23

### Verdict

`APPROVE`

Tracking query generation is implemented. IntelFiles can generate stable, deduplicated, persisted tracking queries from extraction suggestions, entities, keywords, title, thesis, and signal type. Queries include `source_hint` and `enabled`, and regeneration is idempotent or replace-and-regenerate when requested.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_tracking_queries.py -q
# 5 passed

python -m pytest tests/ -q
# 72 passed

$env:DATABASE_URL='sqlite:///./tmp_p2_01_migration.db'
python -m alembic upgrade head
# upgraded through 0004_tracking_queries

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Query quality is deterministic and conservative. P2-02 should consume only enabled rows and should not fetch broad web data beyond configured source checks.

### Approved Next Step

Start `TASK-P2-02: Scheduled Source Checks`.

---

## TASK-P2-02 Review — 2026-05-23

### Verdict

`APPROVE`

Scheduled source checks are implemented as a limited, testable runner. The runner consumes enabled tracking queries, records `SourceCheckRun` attempts, stores `SourceCheckResult` rows, handles provider failures without crashing the full run, and exposes `POST /api/v1/source-checks/run`.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_source_checks.py -q
# 4 passed

python -m pytest tests/test_tracking_queries.py -q
# 5 passed

python -m pytest tests/ -q
# 76 passed

$env:DATABASE_URL='sqlite:///./tmp_p2_02_migration.db'
alembic upgrade head
# upgraded through 0005_source_checks

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- The default checker is intentionally a no-op so tests remain deterministic. Real providers should be added behind the existing checker interface.
- P2-03 should treat source check results as candidates and use conservative matching before suggesting evidence attachment.

### Approved Next Step

Start `TASK-P2-03: Conservative Match Suggestions`.

---

## TASK-P2-03 Review — 2026-05-23

### Verdict

`APPROVE`

Conservative match suggestions are implemented. Source check results can be scored against their tracking query's intel file, only above-threshold matches create open suggestions, duplicate suggestions are not recreated, and intel file details now show open suggestions.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_match_suggestions.py -q
# 5 passed

python -m pytest tests/test_source_checks.py -q
# 4 passed

python -m pytest tests/ -q
# 81 passed

$env:DATABASE_URL='sqlite:///./tmp_p2_03_migration.db'
alembic upgrade head
# upgraded through 0006_match_suggestions

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Suggestions are intentionally not auto-attached. A future task can convert accepted suggestions into RawItems/evidence with source provenance.
- The first matcher is lexical and deterministic. Later provider metadata, embeddings, and entity graph matches can improve recall.

### Approved Next Step

Start `TASK-P2-04: Dormancy and Resurrection Worker`.

---

## TASK-P2-04 Review — 2026-05-23

### Verdict

`APPROVE`

Dormancy and resurrection worker is implemented. `POST /api/v1/lifecycle/run` scans lifecycle candidates, reuses the existing lifecycle evaluator, marks stale files dormant, resurrects dormant files with recent meaningful evidence, and creates resurrection alerts through the existing alert pipeline.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_lifecycle_worker.py -q
# 4 passed

python -m pytest tests/test_mvp_acceptance.py -q
# 1 passed

python -m pytest tests/ -q
# 85 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- The worker is exposed as a manual endpoint for MVP. A scheduler can call the same service later.
- Suggestion acceptance still needs a conversion path from source check results into RawItems/evidence.

### Approved Next Step

Plan `P3: Provider Integrations and Suggestion Acceptance`.

---

## TASK-P3-01 Review — 2026-05-23

### Verdict

`APPROVE`

Match suggestion acceptance is implemented. An open suggestion can now be accepted through the API or UI, converted into a RawItem, attached as follow-up evidence using the existing evidence flow, and marked accepted. Re-accepting the same suggestion is safe and does not duplicate evidence.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_match_suggestions.py -q
# 8 passed

python -m pytest tests/ -q
# 88 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Accepted suggestions currently create source-check RawItems under a search source. Provider-specific source identity can improve in P3-02.

### Approved Next Step

Start `TASK-P3-02: Source Provider Framework`.

---

## TASK-P3-02 Review — 2026-05-23

### Verdict

`APPROVE`

Source provider framework is implemented. Source checks now have a provider protocol, registry, and provider-backed checker that routes by `tracking_query.source_hint`. Missing providers no-op safely, while provider exceptions are isolated and recorded by the runner.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_source_checks.py -q
# 7 passed

python -m pytest tests/ -q
# 91 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- The default registry is intentionally empty and no-network. Concrete RSS/GitHub/careers providers can now plug into the registry.

### Approved Next Step

Start `TASK-P3-03: Status Override With Reason`.

---

## TASK-P3-03 Review — 2026-05-23

### Verdict

`APPROVE`

Status override with reason is implemented. Analysts can manually set lifecycle status through API/UI, a reason is required, lifecycle snapshots are stored, status-change timeline events are created, and lifecycle alerts still fire for relevant transitions such as dormant to resurrected.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_status_override.py -q
# 4 passed

python -m pytest tests/ -q
# 95 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- Override permissioning should be added with auth/roles in the commercial phase.

### Approved Next Step

Start `TASK-P3-04: Trend Archive Snapshots`.

---

## TASK-P3-04 Review — 2026-05-24

### Verdict

`APPROVE`

Trend archive snapshots are implemented. The archive worker creates or updates one daily snapshot per intel file, preserving lifecycle status, scores, evidence/source counts, and last-seen timestamp. File trend history is available in chronological order.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_trend_archives.py -q
# 4 passed

$env:DATABASE_URL='sqlite:///./tmp_p3_04_migration.db'
alembic upgrade head
# upgraded through 0007_trend_archive_snapshots

python -m pytest tests/ -q
# 99 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- P3-05 should use archive snapshots and recent events to build weekly retrospectives.

### Approved Next Step

Start `TASK-P3-05: Weekly Retrospective Briefing`.

---

## TASK-P3-05 Review — 2026-05-24

### Verdict

`APPROVE`

Weekly retrospective briefing is implemented. The backend exposes `GET /api/v1/briefings/weekly`, with sections for changed files, resurrected signals, verified/debunked files, opportunity gainers, and cooling/noise files. The briefing UI now supports Daily and Weekly modes.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_weekly_briefings.py -q
# 2 passed

python -m pytest tests/ -q
# 101 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- P4 can turn weekly retrospectives into exported reports and notification deliveries.

### P3 Verdict

`APPROVE`

P3 Intelligence Workbench is complete. The product now supports suggestion acceptance, provider extensibility, audited status override, daily trend archives, and weekly retrospectives.

### Approved Next Step

Plan `P4: Commercialization`.

---

## TASK-P4-01 Review — 2026-05-24

### Verdict

`APPROVE`

Auth and workspace foundation is implemented. The app now supports local user/workspace bootstrap, workspace membership listing, workspace-scoped inbox submission, workspace-scoped intel file listing/detail access, and a frontend Workspace page that persists local workspace context.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_auth_workspaces.py -q
# 3 passed

$env:DATABASE_URL='sqlite:///./tmp_p4_01_migration.db'
alembic upgrade head
# upgraded through 0008_auth_workspaces

python -m pytest tests/ -q
# 104 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Follow-Up

- This uses local bootstrap headers for MVP. Production OAuth/JWT sessions can replace it without changing workspace-scoped domain data.

### Approved Next Step

Start `TASK-P4-02: Team Notes and Ownership`.

---

## TASK-P4-02 Review — 2026-05-24

### Verdict

`APPROVE`

Team notes and ownership are implemented. Intel files now support owner assignment, review notes, last-reviewed timestamps, and comment threads with author metadata. Workspace-scoped access is preserved.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_collaboration.py -q
# 4 passed

$env:DATABASE_URL='sqlite:///./tmp_p4_02_migration.db'
alembic upgrade head
# upgraded through 0009_team_collaboration

python -m pytest tests/ -q
# 108 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Approved Next Step

Start `TASK-P4-03: Notification Delivery Layer`.

---

## TASK-P4-03 Review — 2026-05-24

### Verdict

`APPROVE`

Notification delivery layer is implemented. Workspaces can configure delivery channels, pending alerts produce auditable delivery attempts, successful mock delivery marks alerts as sent, and sent alerts are not redelivered.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_notifications.py -q
# 3 passed

$env:DATABASE_URL='sqlite:///./tmp_p4_03_migration.db'
alembic upgrade head
# upgraded through 0010_notification_delivery

python -m pytest tests/ -q
# 111 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Approved Next Step

Start `TASK-P4-04: Report Export`.

---

## TASK-P4-04 Review — 2026-05-24

### Verdict

`APPROVE`

Report export is implemented. Daily and weekly briefings can be exported as Markdown and PDF, and the Briefing UI exposes export links for the selected report mode/window.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_reports.py -q
# 4 passed

python -m pytest tests/ -q
# 115 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### Approved Next Step

Start `TASK-P4-05: Usage Limits and Cost Controls`.

---

## TASK-P4-05 Review — 2026-05-24

### Verdict

`APPROVE`

Usage limits and cost controls are implemented. Workspace usage events are recorded for AI extraction and source checks, monthly usage summaries are exposed, and configurable monthly limits return `429` before cost-sensitive work exceeds quota.

### Validation

Passed:

```powershell
cd backend
python -m pytest tests/test_usage.py -q
# 4 passed

$env:DATABASE_URL='sqlite:///./tmp_p4_05_migration.db'
alembic upgrade head
# upgraded through 0011_usage_events

python -m pytest tests/ -q
# 119 passed

cd apps/web
npm run type-check
# passed

npm run build
# passed
```

### P4 Verdict

`APPROVE`

P4 Commercialization slice is complete. The product now has workspace foundations, team collaboration, notification delivery, report export, and usage controls.

### Approved Next Step

Review post-P4 product hardening backlog.

---

## TASK-H1-01 Review — 2026-05-24

### Verdict

`APPROVE`

Production configuration and security baseline are implemented. CORS origins and app version are configurable, production mode rejects default local database credentials and wildcard origins, Docker Compose is environment-driven, and health responses include version metadata.

### Validation

Passed:

```powershell
pytest backend\tests\test_config.py backend\tests\test_health.py
# 6 passed

pytest backend\tests -q
# 124 passed

cd apps\web
npm run type-check
# passed

npm run build
# passed

docker compose config
# passed
```

---

## TASK-H1-02 Review — 2026-05-24

### Verdict

`APPROVE`

Deployment runbook, release checklist, release validation script, and refreshed AI handoff prompts are implemented. The release validation command is now the standard entry point for pre-release checks.

### Validation

Passed:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# Release validation passed
```

---

## TASK-H1-03 Review — 2026-05-24

### Verdict

`APPROVE`

Observability and backup baseline are implemented. API responses now include `X-Request-Id`, request logs are structured JSON lines, and Compose Postgres backup/restore scripts plus runbook documentation exist.

### Validation

Passed:

```powershell
pytest backend\tests\test_health.py backend\tests\test_config.py
# 6 passed

powershell -NoProfile -Command '<PowerShell parser check for validate/backup/restore scripts>'
# parsed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# Release validation passed
```

---

## TASK-H1-04 Review — 2026-05-24

### Verdict

`APPROVE`

Staging readiness review is complete. The project is ready for a local production-like staging rehearsal, but not ready for public production until hosted deployment target, managed secrets, persistent database/Redis, production auth hardening, hosted backups, and external monitoring are handled.

### Validation

Evidence recorded in:

```text
docs/reviews/staging-readiness-2026-05-24.md
```

### H1 Verdict

`APPROVE`

H1 Product Hardening is complete.

### Approved Next Step

Start `TASK-H2-01: Hosted Staging Target and Deployment Adapter`.

---

## TASK-H2-01 Review — 2026-05-24

### Verdict

`APPROVE`

Hosted staging target and deployment adapter are implemented. Render is selected as the first hosted staging path, with `render.yaml`, platform-specific runbook, target comparison, migration instructions, smoke tests, and secret placeholders.

### Validation

Passed:

```powershell
pytest backend\tests\test_config.py -q
# 6 passed

python -c '<parse render.yaml>'
# parsed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# docker compose config passed
# backend: 125 passed
# frontend type-check passed
# frontend build passed
```

### Approved Next Step

Start `TASK-H2-02: Staging Auth Guard`.

---

## TASK-H2-02 Review — 2026-05-24

### Verdict

`APPROVE`

Staging auth guard is implemented. Production mode now requires `ADMIN_API_KEY`; `/api/v1/auth/bootstrap` requires `X-Admin-Secret` in production; local development bootstrap remains unchanged. Render and runbook documentation now include the secret.

### Validation

Passed:

```powershell
pytest backend\tests\test_config.py backend\tests\test_admin_guard.py -q
# 8 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 127 passed
# frontend type-check passed
# frontend build passed
```

### Approved Next Step

Start `TASK-H2-03: Hosted Staging Smoke Test Script`.

---

## TASK-H2-03 Review — 2026-05-24

### Verdict

`APPROVE`

Hosted staging smoke test script is implemented. The script checks backend health, `X-Request-Id`, bootstrap guard behavior, optional admin-secret bootstrap, and optional frontend availability.

### Validation

Passed:

```powershell
powershell -NoProfile -Command '<PowerShell parser check>'
# parsed validate-release, backup-postgres, restore-postgres, smoke-staging

python -c '<parse render.yaml>'
# parsed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 127 passed
# frontend type-check passed
# frontend build passed
```

---

## TASK-H2-04 Review — 2026-05-24

### Verdict

`APPROVE`

Hosted staging readiness review is complete. The repository is ready for a Render Blueprint deployment; the remaining step requires owner-controlled GitHub/Render access and hosted URLs.

### Evidence

See:

```text
docs/reviews/hosted-staging-readiness-2026-05-24.md
```

### H2 Verdict

`APPROVE_WITH_OWNER_ACTION`

The automated planning, code, docs, and validation work for H2 is complete. Deployment itself requires external account action.

---

## TASK-H3-01 Review — 2026-05-24

### Verdict

`APPROVE`

Workspace membership guard is implemented. In production mode, workspace-scoped routes require `X-Workspace-Id` and a member `X-User-Email`; non-members are rejected. Local development remains compatible with the existing workflow.

### Validation

Passed:

```powershell
pytest backend\tests\test_workspace_access_guard.py backend\tests\test_auth_workspaces.py -q
# 6 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 130 passed
# frontend type-check passed
# frontend build passed
```

### Approved Next Step

Start `TASK-H3-02: Workspace Member Management`.

---

## TASK-H3-02 Review — 2026-05-24

### Verdict

`APPROVE`

Workspace member management is implemented. Admins can add members, members can list members, non-admin member creation is rejected in production, and the Workspace page now includes member list/add controls.

### Validation

Passed:

```powershell
pytest backend\tests\test_workspace_members.py backend\tests\test_workspace_access_guard.py -q
# 5 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 132 passed
# frontend type-check passed
# frontend build passed
```

### Approved Next Step

Start `TASK-H3-03: Staging User Access Token`.

---

## TASK-H3-03 Review — 2026-05-24

### Verdict

`APPROVE`

Staging user access tokens are implemented. Bootstrap and member creation issue one-time visible tokens, only token hashes are stored, frontend sends `X-User-Token`, and production workspace guards require member email plus token.

### Validation

Passed:

```powershell
pytest backend\tests\test_workspace_access_guard.py backend\tests\test_workspace_members.py -q
# 6 passed

alembic upgrade head
# upgraded through 0012_user_access_tokens

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 133 passed
# frontend type-check passed
# frontend build passed
```

---

## TASK-H3-04 Review — 2026-05-24

### Verdict

`APPROVE_WITH_PRODUCTION_AUTH_FOLLOWUP`

Access-control readiness review is complete. The app is suitable for private hosted staging with limited operator access, but still needs real customer-grade authentication before public production.

### Evidence

See:

```text
docs/reviews/access-control-readiness-2026-05-24.md
```

---

## TASK-H4-01 Review — 2026-05-24

### Verdict

`APPROVE`

Admin audit log is implemented. Workspace bootstrap and member upsert actions are recorded in `audit_events`, workspace admins can list audit events, and the Workspace page shows recent audit activity.

### Validation

Passed:

```powershell
pytest backend\tests\test_workspace_members.py -q
# 2 passed

alembic upgrade head
# upgraded through 0013_audit_events

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 133 passed
# frontend type-check passed
# frontend build passed
```

### Follow-Up

`scripts\validate-release.ps1` was hardened to fail on native command nonzero exit codes after a pytest failure exposed a false-green risk.

---

## TASK-H4-02 Review — 2026-05-24

### Verdict

`APPROVE`

Audit log export is implemented. Workspace admins can export audit events as CSV, and the Workspace page downloads the file via authenticated `fetch` so staging access-token headers are preserved.

### Validation

Passed:

```powershell
pytest backend\tests\test_workspace_members.py -q
# 2 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 133 passed
# frontend type-check passed
# frontend build passed
```

---

## TASK-H4-03 Review — 2026-05-24

### Verdict

`APPROVE`

Security response headers are implemented. API responses now include baseline browser hardening headers and `Cache-Control: no-store`.

### Validation

Passed:

```powershell
pytest backend\tests\test_health.py backend\tests\test_workspace_members.py -q
# 3 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 133 passed
# frontend type-check passed
# frontend build passed
```

### Approved Next Step

Start `TASK-H4-04: Environment Readiness Check`.

---

## TASK-H4-04 Review — 2026-05-24

### Verdict

`APPROVE`

Environment readiness check is implemented. The script validates production-like env files for required backend/frontend variables, unsafe default credentials, unsafe origins, missing admin secrets, and live AI key requirements.

### Validation

Passed:

```powershell
powershell -NoProfile -Command '<PowerShell parser check>'
# parsed validate-release, backup-postgres, restore-postgres, smoke-staging, check-env-readiness

powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile tmp.env.production -Mode production
# passed with temporary production-like env file

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 133 passed
# frontend type-check passed
# frontend build passed
```

---

## H4 Operations Review — 2026-05-24

### Verdict

`APPROVE`

H4 Operations is complete for private staging. The project now has audit logging, audit export, security response headers, strict release validation, and environment readiness checks.

### Evidence

See:

```text
docs/reviews/operations-readiness-2026-05-24.md
```

### Approved Next Step

Owner action: deploy Render Blueprint and run hosted smoke test.

---

## TASK-H4-05 Review — 2026-05-24

### Verdict

`APPROVE`

Admin rate limiting is implemented. Production bootstrap requests are throttled by a configurable in-memory fixed-window limiter, suitable for single-instance private staging. The limitation is documented for future multi-instance production replacement.

### Validation

Passed:

```powershell
pytest backend\tests\test_admin_guard.py -q
# 2 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 134 passed
# frontend type-check passed
# frontend build passed
```

### Note

The limiter is intentionally local-process only. Production multi-instance deployments should use Redis, a reverse proxy, or provider-level rate limiting.

---

## TASK-H4-06 Review — 2026-05-24

### Verdict

`APPROVE`

Runtime readiness endpoint is implemented. `/api/v1/ready` checks database connectivity and hosted smoke tests now validate both health and readiness.

### Validation

Passed:

```powershell
pytest backend\tests\test_health.py -q
# 2 passed

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 135 passed
# frontend type-check passed
# frontend build passed
```

---

## TASK-H4-07 Review — 2026-05-24

### Verdict

`APPROVE`

Production env template is implemented. `.env.production.example` now documents production-like settings, and `check-env-readiness.ps1` rejects placeholder values such as `<frontend-host>` and `CHANGE_ME`.

### Validation

Passed:

```powershell
powershell -NoProfile -Command '<PowerShell parser check>'
# parsed

powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile tmp.env.production -Mode production
# passed with temporary production-like env file

powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile .env.production.example -Mode production
# failed as expected because placeholders were present

powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
# backend: 135 passed
# frontend type-check passed
# frontend build passed
```

### Approved Next Step

Start `TASK-H4-08: Predeploy Checklist Script`.

---

## TASK-H4-08 Review — 2026-05-24

### Verdict

`APPROVE`

Predeploy checklist script is implemented. `scripts\predeploy-check.ps1` runs helper script parser checks, environment readiness, and full release validation from one command.

### Validation

Passed:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\predeploy-check.ps1 -EnvFile tmp.env.production -Mode production
# script parser checks passed
# env readiness passed
# backend: 135 passed
# frontend type-check passed
# frontend build passed
```

### Current Next Step

Owner action: deploy Render Blueprint and run hosted smoke test.
