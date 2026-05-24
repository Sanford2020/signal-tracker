from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IntelFile, TrendArchiveSnapshot
from app.schemas.archives import (
    TrendArchiveListData,
    TrendArchiveRunData,
    TrendArchiveRunRequest,
    TrendArchiveSnapshotRead,
)


def _today_utc() -> date:
    return datetime.now(UTC).date()


def _apply_file_state(snapshot: TrendArchiveSnapshot, intel_file: IntelFile) -> None:
    snapshot.status = intel_file.status
    snapshot.heat_score = intel_file.heat_score
    snapshot.credibility_score = intel_file.credibility_score
    snapshot.opportunity_score = intel_file.opportunity_score
    snapshot.risk_score = intel_file.risk_score
    snapshot.evidence_count = intel_file.evidence_count
    snapshot.source_count = intel_file.source_count
    snapshot.last_seen_at = intel_file.last_seen_at


def run_trend_archive_snapshots(
    db: Session,
    payload: TrendArchiveRunRequest,
    *,
    workspace_id: UUID | None = None,
) -> TrendArchiveRunData:
    archive_date = payload.archive_date or _today_utc()
    stmt = select(IntelFile).order_by(IntelFile.updated_at.desc(), IntelFile.id.asc()).limit(payload.limit)
    if workspace_id is not None:
        stmt = stmt.where(IntelFile.workspace_id == workspace_id)
    intel_files = db.scalars(stmt).all()

    created_count = 0
    updated_count = 0
    snapshots: list[TrendArchiveSnapshot] = []
    for intel_file in intel_files:
        snapshot = db.scalar(
            select(TrendArchiveSnapshot).where(
                TrendArchiveSnapshot.intel_file_id == intel_file.id,
                TrendArchiveSnapshot.archive_date == archive_date,
            )
        )
        if snapshot is None:
            snapshot = TrendArchiveSnapshot(
                intel_file_id=intel_file.id,
                archive_date=archive_date,
                status=intel_file.status,
                heat_score=intel_file.heat_score,
                credibility_score=intel_file.credibility_score,
                opportunity_score=intel_file.opportunity_score,
                risk_score=intel_file.risk_score,
                evidence_count=intel_file.evidence_count,
                source_count=intel_file.source_count,
                last_seen_at=intel_file.last_seen_at,
            )
            db.add(snapshot)
            created_count += 1
        else:
            _apply_file_state(snapshot, intel_file)
            updated_count += 1
        snapshots.append(snapshot)

    db.commit()
    for snapshot in snapshots:
        db.refresh(snapshot)

    return TrendArchiveRunData(
        archive_date=archive_date,
        checked_count=len(intel_files),
        created_count=created_count,
        updated_count=updated_count,
        items=[TrendArchiveSnapshotRead.model_validate(item) for item in snapshots],
    )


def list_trend_archive_snapshots(
    db: Session,
    intel_file_id: UUID,
    *,
    workspace_id: UUID | None = None,
) -> TrendArchiveListData:
    intel_file = db.scalar(select(IntelFile).where(IntelFile.id == intel_file_id))
    if intel_file is None or (workspace_id is not None and intel_file.workspace_id != workspace_id):
        raise ValueError("Intel file not found.")

    snapshots = db.scalars(
        select(TrendArchiveSnapshot)
        .where(TrendArchiveSnapshot.intel_file_id == intel_file_id)
        .order_by(TrendArchiveSnapshot.archive_date.asc())
    ).all()

    return TrendArchiveListData(
        items=[TrendArchiveSnapshotRead.model_validate(item) for item in snapshots],
        total=len(snapshots),
    )
