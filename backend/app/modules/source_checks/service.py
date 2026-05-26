from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IntelFile, SourceCheckResult, SourceCheckRun, TrackingQuery
from app.modules.usage.service import SOURCE_CHECK, assert_usage_available, record_usage
from app.schemas.source_checks import SourceCheckRunData, SourceCheckRunRequest, SourceProviderHealthRead


@dataclass(frozen=True)
class CheckerResult:
    title: str
    url: str | None = None
    snippet: str | None = None
    source_name: str | None = None
    raw: dict[str, Any] | None = None


class SourceChecker(Protocol):
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        """Return candidate source results for one tracking query."""


class NoopSourceChecker:
    def search(self, query: TrackingQuery) -> Sequence[CheckerResult]:
        return []


def run_source_checks(
    db: Session,
    payload: SourceCheckRunRequest,
    checker: SourceChecker | None = None,
    workspace_id: UUID | None = None,
) -> SourceCheckRunData:
    active_checker = checker or NoopSourceChecker()
    started_at = datetime.now(UTC)
    run = SourceCheckRun(status="running", started_at=started_at, workspace_id=workspace_id)
    db.add(run)
    db.flush()

    query_stmt = select(TrackingQuery).where(TrackingQuery.enabled.is_(True))
    if workspace_id is not None:
        query_stmt = query_stmt.join(IntelFile, IntelFile.id == TrackingQuery.intel_file_id).where(
            IntelFile.workspace_id == workspace_id
        )
    queries = db.scalars(query_stmt.order_by(TrackingQuery.created_at.asc(), TrackingQuery.id.asc()).limit(payload.limit)).all()

    assert_usage_available(
        db,
        workspace_id=workspace_id,
        usage_type=SOURCE_CHECK,
        amount=len(queries),
    )

    result_count = 0
    errors: list[str] = []
    for query in queries:
        try:
            checker_results = active_checker.search(query)
        except Exception as exc:  # noqa: BLE001 - worker records per-query failures and keeps going.
            errors.append(f"{query.id}: {exc}")
            continue

        for item in checker_results:
            result = SourceCheckResult(
                run_id=run.id,
                tracking_query_id=query.id,
                title=item.title,
                url=item.url,
                snippet=item.snippet,
                source_name=item.source_name,
                source_hint=query.source_hint,
                raw=item.raw,
            )
            db.add(result)
            result_count += 1

    run.checked_query_count = len(queries)
    run.result_count = result_count
    run.finished_at = datetime.now(UTC)
    run.error = "\n".join(errors) if errors else None
    if errors and result_count == 0:
        run.status = "failed"
    elif errors:
        run.status = "partial"
    else:
        run.status = "completed"

    if queries:
        record_usage(
            db,
            workspace_id=workspace_id,
            usage_type=SOURCE_CHECK,
            amount=len(queries),
            meta={"source_check_run_id": str(run.id)},
        )
    db.commit()
    db.refresh(run)
    results = db.scalars(
        select(SourceCheckResult)
        .where(SourceCheckResult.run_id == run.id)
        .order_by(SourceCheckResult.checked_at.asc(), SourceCheckResult.id.asc())
    ).all()
    return SourceCheckRunData(run=run, results=list(results))


def list_source_check_runs(
    db: Session,
    *,
    limit: int = 10,
    workspace_id: UUID | None = None,
) -> list[SourceCheckRun]:
    capped_limit = min(max(limit, 1), 50)
    stmt = select(SourceCheckRun).order_by(SourceCheckRun.started_at.desc(), SourceCheckRun.id.desc()).limit(capped_limit)
    if workspace_id is not None:
        stmt = stmt.where(SourceCheckRun.workspace_id == workspace_id)
    return list(
        db.scalars(stmt).all()
    )


def summarize_source_provider_health(
    db: Session,
    *,
    limit: int = 25,
    workspace_id: UUID | None = None,
) -> list[SourceProviderHealthRead]:
    capped_limit = min(max(limit, 1), 100)
    query_stmt = select(TrackingQuery).where(TrackingQuery.enabled.is_(True))
    if workspace_id is not None:
        query_stmt = query_stmt.join(IntelFile, IntelFile.id == TrackingQuery.intel_file_id).where(
            IntelFile.workspace_id == workspace_id
        )
    queries = db.scalars(query_stmt).all()

    health_by_hint: dict[str, SourceProviderHealthRead] = {}
    for query in queries:
        source_hint = query.source_hint or "unknown"
        current = health_by_hint.get(source_hint)
        health_by_hint[source_hint] = SourceProviderHealthRead(
            source_hint=source_hint,
            enabled_query_count=(current.enabled_query_count if current else 0) + 1,
            recent_result_count=current.recent_result_count if current else 0,
            last_result_at=current.last_result_at if current else None,
            latest_run_status=current.latest_run_status if current else None,
            latest_run_error=current.latest_run_error if current else None,
        )

    run_stmt = select(SourceCheckRun).order_by(SourceCheckRun.started_at.desc(), SourceCheckRun.id.desc()).limit(capped_limit)
    if workspace_id is not None:
        run_stmt = run_stmt.where(SourceCheckRun.workspace_id == workspace_id)
    runs = list(db.scalars(run_stmt).all())
    latest_run = runs[0] if runs else None
    run_ids = [run.id for run in runs]

    if run_ids:
        results = db.scalars(
            select(SourceCheckResult)
            .where(SourceCheckResult.run_id.in_(run_ids))
            .order_by(SourceCheckResult.checked_at.desc(), SourceCheckResult.id.desc())
        ).all()
        for result in results:
            source_hint = result.source_hint or result.source_name or "unknown"
            current = health_by_hint.get(source_hint)
            health_by_hint[source_hint] = SourceProviderHealthRead(
                source_hint=source_hint,
                enabled_query_count=current.enabled_query_count if current else 0,
                recent_result_count=(current.recent_result_count if current else 0) + 1,
                last_result_at=max(
                    [value for value in [current.last_result_at if current else None, result.checked_at] if value is not None]
                ),
                latest_run_status=current.latest_run_status if current else None,
                latest_run_error=current.latest_run_error if current else None,
            )

    if latest_run is not None:
        health_by_hint = {
            key: SourceProviderHealthRead(
                source_hint=item.source_hint,
                enabled_query_count=item.enabled_query_count,
                recent_result_count=item.recent_result_count,
                last_result_at=item.last_result_at,
                latest_run_status=latest_run.status,
                latest_run_error=latest_run.error,
            )
            for key, item in health_by_hint.items()
        }

    return sorted(
        health_by_hint.values(),
        key=lambda item: (item.enabled_query_count == 0, -item.recent_result_count, item.source_hint),
    )
