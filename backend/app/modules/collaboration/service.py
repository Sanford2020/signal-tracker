from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import IntelFile, IntelFileComment, User
from app.schemas.collaboration import (
    IntelFileCollaborationData,
    IntelFileCollaborationRead,
    IntelFileCollaborationUpdateRequest,
    IntelFileCommentCreateData,
    IntelFileCommentCreateRequest,
    IntelFileCommentListData,
    IntelFileCommentRead,
)


def _load_file(db: Session, intel_file_id: UUID, workspace_id: UUID | None) -> IntelFile:
    intel_file = db.get(IntelFile, intel_file_id)
    if intel_file is None or (workspace_id is not None and intel_file.workspace_id != workspace_id):
        raise ValueError("Intel file not found.")
    return intel_file


def _read_collaboration(intel_file: IntelFile) -> IntelFileCollaborationRead:
    return IntelFileCollaborationRead(
        intel_file_id=intel_file.id,
        owner_user_id=intel_file.owner_user_id,
        review_note=intel_file.review_note,
        last_reviewed_at=intel_file.last_reviewed_at,
    )


def update_intel_file_collaboration(
    db: Session,
    intel_file_id: UUID,
    payload: IntelFileCollaborationUpdateRequest,
    *,
    workspace_id: UUID | None = None,
) -> IntelFileCollaborationData:
    intel_file = _load_file(db, intel_file_id, workspace_id)
    if payload.owner_user_id is not None and db.get(User, payload.owner_user_id) is None:
        raise ValueError("Owner user not found.")

    intel_file.owner_user_id = payload.owner_user_id
    intel_file.review_note = payload.review_note.strip() if payload.review_note else None
    if payload.mark_reviewed:
        intel_file.last_reviewed_at = datetime.now(UTC)

    db.commit()
    db.refresh(intel_file)
    return IntelFileCollaborationData(item=_read_collaboration(intel_file))


def _comment_read(comment: IntelFileComment) -> IntelFileCommentRead:
    author = comment.author
    return IntelFileCommentRead(
        id=comment.id,
        intel_file_id=comment.intel_file_id,
        author_user_id=comment.author_user_id,
        author_email=author.email if author else "unknown",
        author_name=author.name if author else "Unknown",
        body=comment.body,
        created_at=comment.created_at,
    )


def list_intel_file_comments(
    db: Session,
    intel_file_id: UUID,
    *,
    workspace_id: UUID | None = None,
) -> IntelFileCommentListData:
    _load_file(db, intel_file_id, workspace_id)
    comments = db.scalars(
        select(IntelFileComment)
        .options(selectinload(IntelFileComment.author))
        .where(IntelFileComment.intel_file_id == intel_file_id)
        .order_by(IntelFileComment.created_at.asc(), IntelFileComment.id.asc())
    ).all()
    return IntelFileCommentListData(items=[_comment_read(item) for item in comments], total=len(comments))


def create_intel_file_comment(
    db: Session,
    intel_file_id: UUID,
    payload: IntelFileCommentCreateRequest,
    *,
    author_email: str | None,
    workspace_id: UUID | None = None,
) -> IntelFileCommentCreateData:
    if not author_email:
        raise PermissionError("X-User-Email header is required.")
    intel_file = _load_file(db, intel_file_id, workspace_id)
    user = db.scalar(select(User).where(User.email == author_email.strip().lower()))
    if user is None:
        raise PermissionError("Comment author not found.")

    comment = IntelFileComment(
        intel_file_id=intel_file.id,
        author_user_id=user.id,
        body=payload.body.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    comment = db.scalar(
        select(IntelFileComment)
        .options(selectinload(IntelFileComment.author))
        .where(IntelFileComment.id == comment.id)
    )
    assert comment is not None
    return IntelFileCommentCreateData(item=_comment_read(comment))
