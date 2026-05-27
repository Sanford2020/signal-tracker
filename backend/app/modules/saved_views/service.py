import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IntelFileSavedView
from app.schemas.saved_views import (
    IntelFileSavedViewCreateRequest,
    IntelFileSavedViewData,
    IntelFileSavedViewDeleteData,
    IntelFileSavedViewListData,
    IntelFileSavedViewRead,
    IntelFileSavedViewUpdateRequest,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = _SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug or "saved-view"


def _to_read(view: IntelFileSavedView) -> IntelFileSavedViewRead:
    return IntelFileSavedViewRead.model_validate(view)


def _clear_default_views(db: Session, *, workspace_id: UUID | None, except_view_id: UUID | None = None) -> None:
    stmt = select(IntelFileSavedView).where(
        IntelFileSavedView.workspace_id == workspace_id,
        IntelFileSavedView.is_default.is_(True),
    )
    if except_view_id is not None:
        stmt = stmt.where(IntelFileSavedView.id != except_view_id)
    for view in db.scalars(stmt).all():
        view.is_default = False


def list_intel_file_saved_views(
    db: Session,
    *,
    workspace_id: UUID | None = None,
) -> IntelFileSavedViewListData:
    stmt = select(IntelFileSavedView).where(IntelFileSavedView.workspace_id == workspace_id)
    rows = db.scalars(stmt.order_by(IntelFileSavedView.updated_at.desc(), IntelFileSavedView.name.asc())).all()
    return IntelFileSavedViewListData(items=[_to_read(row) for row in rows], total=len(rows))


def upsert_intel_file_saved_view(
    db: Session,
    payload: IntelFileSavedViewCreateRequest,
    *,
    workspace_id: UUID | None = None,
    actor_email: str | None = None,
) -> IntelFileSavedViewData:
    name = payload.name.strip()
    slug = _slugify(name)
    view = db.scalar(
        select(IntelFileSavedView).where(
            IntelFileSavedView.workspace_id == workspace_id,
            IntelFileSavedView.slug == slug,
        )
    )
    if view is None:
        view = IntelFileSavedView(
            workspace_id=workspace_id,
            name=name,
            slug=slug,
            filters=payload.filters.model_dump(),
            is_default=payload.is_default,
            created_by_email=actor_email.strip().lower() if actor_email else None,
        )
        db.add(view)
    else:
        view.name = name
        view.filters = payload.filters.model_dump()
        if payload.is_default:
            view.is_default = True
        if actor_email:
            view.created_by_email = actor_email.strip().lower()
    if payload.is_default:
        db.flush()
        _clear_default_views(db, workspace_id=workspace_id, except_view_id=view.id)
    db.commit()
    db.refresh(view)
    return IntelFileSavedViewData(item=_to_read(view))


def update_intel_file_saved_view(
    db: Session,
    view_id: UUID,
    payload: IntelFileSavedViewUpdateRequest,
    *,
    workspace_id: UUID | None = None,
    actor_email: str | None = None,
) -> IntelFileSavedViewData:
    view = db.scalar(
        select(IntelFileSavedView).where(
            IntelFileSavedView.id == view_id,
            IntelFileSavedView.workspace_id == workspace_id,
        )
    )
    if view is None:
        raise ValueError("Saved view not found.")

    if payload.name is not None:
        name = payload.name.strip()
        slug = _slugify(name)
        existing = db.scalar(
            select(IntelFileSavedView).where(
                IntelFileSavedView.workspace_id == workspace_id,
                IntelFileSavedView.slug == slug,
                IntelFileSavedView.id != view_id,
            )
        )
        if existing is not None:
            raise ValueError("Saved view name already exists.")
        view.name = name
        view.slug = slug

    if payload.filters is not None:
        view.filters = payload.filters.model_dump()

    if payload.is_default is not None:
        view.is_default = payload.is_default
        if payload.is_default:
            _clear_default_views(db, workspace_id=workspace_id, except_view_id=view.id)

    if actor_email:
        view.created_by_email = actor_email.strip().lower()

    db.commit()
    db.refresh(view)
    return IntelFileSavedViewData(item=_to_read(view))


def delete_intel_file_saved_view(
    db: Session,
    view_id: UUID,
    *,
    workspace_id: UUID | None = None,
) -> IntelFileSavedViewDeleteData:
    view = db.scalar(
        select(IntelFileSavedView).where(
            IntelFileSavedView.id == view_id,
            IntelFileSavedView.workspace_id == workspace_id,
        )
    )
    if view is None:
        raise ValueError("Saved view not found.")
    db.delete(view)
    db.commit()
    return IntelFileSavedViewDeleteData(deleted_id=view_id)
