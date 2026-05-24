from fastapi import Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import get_settings, verify_admin_secret
from app.core.rate_limit import RateLimitExceededError, check_fixed_window_rate_limit
from app.modules.auth.service import ensure_workspace_access, ensure_workspace_role


def require_admin_secret(
    x_admin_secret: str | None = Header(None, alias="X-Admin-Secret"),
) -> None:
    settings = get_settings()
    if verify_admin_secret(x_admin_secret, settings):
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="X-Admin-Secret is required for this operation.",
    )


def require_admin_rate_limit(request: Request) -> None:
    settings = get_settings()
    if settings.app_env.lower() != "production":
        return
    client_host = request.client.host if request.client else "unknown"
    key = f"admin:{request.url.path}:{client_host}"
    try:
        check_fixed_window_rate_limit(key=key, limit=settings.admin_rate_limit_per_minute)
    except RateLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Admin rate limit exceeded.",
        ) from exc


def require_workspace_access(
    db: Session,
    workspace_id: UUID | None,
    user_email: str | None,
    user_token: str | None = None,
) -> None:
    try:
        ensure_workspace_access(db, workspace_id, user_email, user_token)
    except PermissionError as exc:
        status_code = (
            status.HTTP_401_UNAUTHORIZED
            if "header is required" in str(exc).lower()
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def require_workspace_admin(
    db: Session,
    workspace_id: UUID | None,
    user_email: str | None,
    user_token: str | None = None,
) -> None:
    try:
        ensure_workspace_role(db, workspace_id, user_email, user_token, {"admin"})
    except PermissionError as exc:
        status_code = (
            status.HTTP_401_UNAUTHORIZED
            if "header is required" in str(exc).lower()
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
