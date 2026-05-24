from uuid import UUID

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.match_suggestions.service import generate_match_suggestions_for_run
from app.modules.source_checks.providers import ProviderBackedSourceChecker, get_default_provider_registry
from app.modules.source_checks.service import run_source_checks
from app.modules.usage.service import UsageLimitError
from app.schemas.api import ApiError, ApiResponse
from app.schemas.match_suggestions import MatchSuggestionGenerateData, MatchSuggestionGenerateRequest
from app.schemas.source_checks import SourceCheckRunData, SourceCheckRunRequest

router = APIRouter(prefix="/source-checks", tags=["source-checks"])


@router.post("/run", response_model=ApiResponse[SourceCheckRunData])
def run_source_checks_route(
    payload: SourceCheckRunRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[SourceCheckRunData] | JSONResponse:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        checker = ProviderBackedSourceChecker(get_default_provider_registry())
        data = run_source_checks(db, payload, checker=checker, workspace_id=x_workspace_id)
    except ValueError as exc:
        return JSONResponse(
            status_code=404,
            content=ApiResponse[SourceCheckRunData](
                success=False,
                data=None,
                error=ApiError(code="not_found", message=str(exc)),
            ).model_dump(),
        )
    except UsageLimitError as exc:
        return JSONResponse(
            status_code=429,
            content=ApiResponse[SourceCheckRunData](
                success=False,
                data=None,
                error=ApiError(code="usage_limit_exceeded", message=str(exc)),
            ).model_dump(),
        )
    return ApiResponse(success=True, data=data, error=None)


@router.post("/runs/{run_id}/match-suggestions", response_model=ApiResponse[MatchSuggestionGenerateData])
def generate_match_suggestions_route(
    run_id: UUID,
    payload: MatchSuggestionGenerateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[MatchSuggestionGenerateData]:
    data = generate_match_suggestions_for_run(db, run_id, payload)
    return ApiResponse(success=True, data=data, error=None)
