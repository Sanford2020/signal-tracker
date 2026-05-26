from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.match_suggestions.service import accept_match_suggestion, update_match_suggestion_status
from app.schemas.api import ApiResponse
from app.schemas.match_suggestions import (
    MatchSuggestionAcceptData,
    MatchSuggestionAcceptRequest,
    MatchSuggestionStatusUpdateData,
    MatchSuggestionStatusUpdateRequest,
)

router = APIRouter(prefix="/match-suggestions", tags=["match-suggestions"])


@router.post("/{suggestion_id}/accept", response_model=ApiResponse[MatchSuggestionAcceptData])
def accept_match_suggestion_route(
    suggestion_id: UUID,
    payload: MatchSuggestionAcceptRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[MatchSuggestionAcceptData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = accept_match_suggestion(db, suggestion_id, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.patch("/{suggestion_id}", response_model=ApiResponse[MatchSuggestionStatusUpdateData])
def update_match_suggestion_route(
    suggestion_id: UUID,
    payload: MatchSuggestionStatusUpdateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[MatchSuggestionStatusUpdateData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = update_match_suggestion_status(db, suggestion_id, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)
