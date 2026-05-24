from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IntelFile, SourceCheckResult, SourceCheckRun, TrackingQuery
from app.modules.usage.service import SOURCE_CHECK, assert_usage_available, record_usage
from app.schemas.source_checks import SourceCheckRunData, SourceCheckRunRequest


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
    workspace_id=None,
) -> SourceCheckRunData:
    active_checker = checker or NoopSourceChecker()
    started_at = datetime.now(UTC)
    run = SourceCheckRun(status="running", started_at=started_at)
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


def list_source_check_runs(db: Session, *, limit: int = 10) -> list[SourceCheckRun]:
    capped_limit = min(max(limit, 1), 50)
    return list(
        db.scalars(
            select(SourceCheckRun)
            .order_by(SourceCheckRun.started_at.desc(), SourceCheckRun.id.desc())
            .limit(capped_limit)
        ).all()
    )
