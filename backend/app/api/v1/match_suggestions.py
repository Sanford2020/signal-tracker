from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.match_suggestions.service import accept_match_suggestion
from app.schemas.api import ApiResponse
from app.schemas.match_suggestions import MatchSuggestionAcceptData, MatchSuggestionAcceptRequest

router = APIRouter(prefix="/match-suggestions", tags=["match-suggestions"])


@router.post("/{suggestion_id}/accept", response_model=ApiResponse[MatchSuggestionAcceptData])
def accept_match_suggestion_route(
    suggestion_id: UUID,
    payload: MatchSuggestionAcceptRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[MatchSuggestionAcceptData]:
    try:
        data = accept_match_suggestion(db, suggestion_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)
