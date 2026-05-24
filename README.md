# Signal Tracker

Signal Tracker is an early-signal intelligence lifecycle tracking system.

It is not a normal news reader. The product goal is to capture weak signals when they first appear, turn them into durable intelligence files, and track whether they spread, cool down, revive, get verified, get debunked, or become opportunities.

## Core Loop

```text
Discover signal
  -> Create intel file
  -> Attach evidence
  -> Track follow-up events
  -> Update lifecycle state
  -> Score opportunity and risk
  -> Alert on meaningful changes
  -> Brief the operator
```

## Planning Documents

| Document | Purpose |
| --- | --- |
| [AI_START_HERE.md](./AI_START_HERE.md) | First file for external AI implementation agents |
| [EXTERNAL_AI_PROMPT.md](./EXTERNAL_AI_PROMPT.md) | Copy-paste prompt for another AI coding tool |
| [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) | One-page project direction and constraints |
| [docs/prd.md](./docs/prd.md) | Product requirements and MVP scope |
| [docs/commercial-prd.md](./docs/commercial-prd.md) | Commercial product requirements after MVP |
| [docs/architecture/system-architecture.md](./docs/architecture/system-architecture.md) | System modules, data flow, and deployment shape |
| [docs/architecture/data-model.md](./docs/architecture/data-model.md) | Core domain entities and relationships |
| [docs/methodology/lifecycle-methodology.md](./docs/methodology/lifecycle-methodology.md) | Signal lifecycle definitions and state machine |
| [docs/methodology/scoring-methodology.md](./docs/methodology/scoring-methodology.md) | Heat, credibility, opportunity, and risk scoring |
| [docs/methodology/source-taxonomy.md](./docs/methodology/source-taxonomy.md) | Source and signal classification |
| [docs/plans/ai-employee-execution-plan.md](./docs/plans/ai-employee-execution-plan.md) | Execution plan for AI employees |
| [docs/specs/api-contracts.md](./docs/specs/api-contracts.md) | MVP API contracts |
| [docs/specs/ui-spec.md](./docs/specs/ui-spec.md) | MVP UI requirements |
| [docs/specs/ai-extraction-contract.md](./docs/specs/ai-extraction-contract.md) | Structured AI extraction contract |
| [docs/specs/acceptance-gates.md](./docs/specs/acceptance-gates.md) | Milestone acceptance gates |
| [docs/handoff/owner-handoff.md](./docs/handoff/owner-handoff.md) | Owner handoff and next AI prompt |
| [docs/handoff/implementation-kickoff.md](./docs/handoff/implementation-kickoff.md) | Implementation kickoff handoff after P0 review |
| [docs/runbooks/deployment.md](./docs/runbooks/deployment.md) | Staging and production-like deployment runbook |
| [docs/runbooks/hosted-staging-render.md](./docs/runbooks/hosted-staging-render.md) | Render hosted staging deployment path |
| [docs/runbooks/release-checklist.md](./docs/runbooks/release-checklist.md) | Release, rollback, and operations checklist |
| [docs/runbooks/observability-backup.md](./docs/runbooks/observability-backup.md) | Request tracing and Postgres backup/restore baseline |
| [docs/reviews/staging-readiness-2026-05-24.md](./docs/reviews/staging-readiness-2026-05-24.md) | Current staging readiness verdict and remaining gaps |
| [docs/reviews/hosted-staging-readiness-2026-05-24.md](./docs/reviews/hosted-staging-readiness-2026-05-24.md) | Render Blueprint deploy readiness and owner actions |
| [docs/reviews/access-control-readiness-2026-05-24.md](./docs/reviews/access-control-readiness-2026-05-24.md) | Staging access-control verdict and production auth gaps |
| [docs/reviews/operations-readiness-2026-05-24.md](./docs/reviews/operations-readiness-2026-05-24.md) | Private staging operations baseline and remaining production gaps |
| [openspec/README.md](./openspec/README.md) | OpenSpec-inspired change workflow |
| [DECISIONS.md](./DECISIONS.md) | Architecture decision records |
| [TASKS.md](./TASKS.md) | AI task board |
| [AGENTS.md](./AGENTS.md) | AI development operating rules |
| [SKILLS.md](./SKILLS.md) | Skill roles and boundaries |

## Local Development

See [docs/runbooks/local-dev.md](./docs/runbooks/local-dev.md) for startup and validation commands.

Quick validation:

```powershell
docker compose up -d db redis
cd backend && python -m pytest tests/ -q
cd ..\apps\web && npm run type-check && npm run build
```

Release validation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-release.ps1
```

GitHub Actions also runs backend `pytest`, frontend `npm run type-check`, and frontend `npm run build` on `main` pushes and pull requests.

Hosted staging smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-staging.ps1 -ApiBaseUrl "https://<api>" -WebBaseUrl "https://<web>"
```

Environment readiness:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-env-readiness.ps1 -EnvFile ".env.production" -Mode production
```

Use `.env.production.example` as the production-like template; it is expected to fail readiness checks until placeholders are replaced.

Predeploy check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\predeploy-check.ps1 -EnvFile ".env.production" -Mode production
```

Production guardrails:

- Set `APP_ENV=production`.
- Replace the default local `DATABASE_URL` credentials.
- Set `ALLOWED_ORIGINS` to explicit trusted origins, for example `https://app.example.com`.
- Set `ADMIN_API_KEY` and use it through `X-Admin-Secret` for bootstrap/admin operations.
- Wildcard origins and default local database credentials are rejected in production mode.
- API responses include `X-Request-Id`; keep this value when debugging production issues.
- Production workspace-scoped requests require `X-User-Email` and `X-User-Token`.

## Repository Layout

```text
backend/     FastAPI API + Alembic
apps/web/    Next.js frontend shell
workers/     Celery worker skeleton
docker-compose.yml
scripts/     Local dev helpers
```

## AI Employee Kickoff

P0-P4 and H1 product hardening are complete. The current track is H2 hosted staging; see [NEXT_TASK.md](./NEXT_TASK.md) for the next executable assignment.

Implementation tasks should use the matching change package under `openspec/changes/`.

## Development Principle

Do not start implementation before the first milestone planning docs are accepted.

The first build milestone is not "a news app". It is:

```text
Manual link submission
  -> structured signal extraction
  -> intel file creation
  -> evidence timeline
  -> lifecycle status update
  -> daily briefing
```
