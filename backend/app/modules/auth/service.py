import re
import secrets
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import User, Workspace, WorkspaceMembership
from app.modules.audit.service import record_audit_event
from app.schemas.auth import (
    BootstrapData,
    BootstrapRequest,
    WorkspaceListData,
    WorkspaceMemberCreateData,
    WorkspaceMemberCreateRequest,
    WorkspaceMemberListData,
    WorkspaceMemberRead,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = _SLUG_RE.sub("-", value.strip().lower()).strip("-")
    return slug or "workspace"


def _unique_slug(db: Session, name: str) -> str:
    base = _slugify(name)
    slug = base
    counter = 2
    while db.scalar(select(Workspace).where(Workspace.slug == slug)) is not None:
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _hash_access_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def _issue_access_token(user: User) -> str:
    token = secrets.token_urlsafe(32)
    user.access_token_hash = _hash_access_token(token)
    user.access_token_hint = token[-8:]
    return token


def verify_user_access_token(user: User, provided_token: str | None) -> bool:
    if not user.access_token_hash or not provided_token:
        return False
    return secrets.compare_digest(user.access_token_hash, _hash_access_token(provided_token))


def bootstrap_workspace(db: Session, payload: BootstrapRequest) -> BootstrapData:
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, name=payload.name.strip())
        db.add(user)
        db.flush()
    access_token = _issue_access_token(user)

    workspace = Workspace(name=payload.workspace_name.strip(), slug=_unique_slug(db, payload.workspace_name))
    db.add(workspace)
    db.flush()

    membership = WorkspaceMembership(workspace_id=workspace.id, user_id=user.id, role="admin")
    db.add(membership)
    record_audit_event(
        db,
        action="workspace.bootstrap",
        workspace_id=workspace.id,
        actor_email=email,
        target_type="workspace",
        target_id=str(workspace.id),
        metadata={"workspace_name": workspace.name},
    )
    db.commit()
    db.refresh(user)
    db.refresh(workspace)
    db.refresh(membership)
    return BootstrapData(user=user, workspace=workspace, membership=membership, access_token=access_token)


def _to_workspace_member_read(membership: WorkspaceMembership) -> WorkspaceMemberRead:
    user = membership.user
    return WorkspaceMemberRead(
        membership_id=membership.id,
        user_id=membership.user_id,
        email=user.email if user else "unknown",
        name=user.name if user else "Unknown",
        role=membership.role,
        joined_at=membership.created_at,
    )


def list_workspaces(db: Session, user_email: str | None = None) -> WorkspaceListData:
    query = select(Workspace)
    if user_email:
        query = (
            query.join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(User.email == user_email.strip().lower())
        )
    items = db.scalars(query.order_by(Workspace.created_at.desc(), Workspace.id.asc())).all()
    return WorkspaceListData(items=list(items), total=len(items))


def list_workspace_members(db: Session, workspace_id: UUID) -> WorkspaceMemberListData:
    memberships = db.scalars(
        select(WorkspaceMembership)
        .join(User, User.id == WorkspaceMembership.user_id)
        .where(WorkspaceMembership.workspace_id == workspace_id)
        .order_by(WorkspaceMembership.created_at.asc(), User.email.asc())
    ).all()
    return WorkspaceMemberListData(
        items=[_to_workspace_member_read(item) for item in memberships],
        total=len(memberships),
    )


def add_workspace_member(
    db: Session,
    workspace_id: UUID,
    payload: WorkspaceMemberCreateRequest,
    *,
    actor_email: str | None = None,
) -> WorkspaceMemberCreateData:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise ValueError("Workspace not found.")

    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, name=payload.name.strip())
        db.add(user)
        db.flush()
    else:
        user.name = payload.name.strip()
    access_token = _issue_access_token(user)

    membership = db.scalar(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user.id,
        )
    )
    if membership is None:
        membership = WorkspaceMembership(
            workspace_id=workspace_id,
            user_id=user.id,
            role=payload.role,
        )
        db.add(membership)
    else:
        membership.role = payload.role

    record_audit_event(
        db,
        action="workspace.member.upsert",
        workspace_id=workspace_id,
        actor_email=actor_email,
        target_type="user",
        target_id=str(user.id),
        metadata={"member_email": email, "role": payload.role},
    )
    db.commit()
    db.refresh(membership)
    return WorkspaceMemberCreateData(member=_to_workspace_member_read(membership), access_token=access_token)


def ensure_workspace_exists(db: Session, workspace_id: UUID | None) -> Workspace | None:
    if workspace_id is None:
        return None
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise ValueError("Workspace not found.")
    return workspace


def ensure_workspace_access(
    db: Session,
    workspace_id: UUID | None,
    user_email: str | None,
    user_token: str | None = None,
) -> Workspace | None:
    workspace = ensure_workspace_exists(db, workspace_id)
    settings = get_settings()
    if settings.app_env.lower() != "production":
        return workspace

    if workspace_id is None:
        raise PermissionError("X-Workspace-Id header is required.")
    if not user_email:
        raise PermissionError("X-User-Email header is required.")

    membership = db.scalar(
        select(WorkspaceMembership)
        .join(User, User.id == WorkspaceMembership.user_id)
        .where(
            WorkspaceMembership.workspace_id == workspace_id,
            User.email == user_email.strip().lower(),
        )
    )
    if membership is None:
        raise PermissionError("User is not a member of this workspace.")
    if not membership.user or not verify_user_access_token(membership.user, user_token):
        raise PermissionError("X-User-Token header is required.")
    return workspace


def ensure_workspace_role(
    db: Session,
    workspace_id: UUID | None,
    user_email: str | None,
    user_token: str | None,
    allowed_roles: set[str],
) -> Workspace | None:
    workspace = ensure_workspace_access(db, workspace_id, user_email, user_token)
    settings = get_settings()
    if settings.app_env.lower() != "production":
        return workspace

    membership = db.scalar(
        select(WorkspaceMembership)
        .join(User, User.id == WorkspaceMembership.user_id)
        .where(
            WorkspaceMembership.workspace_id == workspace_id,
            User.email == user_email.strip().lower() if user_email else False,
        )
    )
    if membership is None or membership.role not in allowed_roles:
        raise PermissionError("User does not have the required workspace role.")
    return workspace
