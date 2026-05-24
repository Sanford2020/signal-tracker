from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.models.enums import LifecycleStatus
from app.modules.intel_files.service import (
    EvidenceConflictError,
    IntelFileError,
    attach_evidence,
    create_intel_file,
    get_intel_file_detail,
    list_intel_files,
    to_intel_file_summary,
)
from app.modules.archives.service import list_trend_archive_snapshots
from app.modules.auth.service import ensure_workspace_exists
from app.modules.collaboration.service import (
    create_intel_file_comment,
    list_intel_file_comments,
    update_intel_file_collaboration,
)
from app.modules.lifecycle.service import evaluate_intel_file, override_intel_file_status
from app.modules.match_suggestions.service import list_match_suggestions
from app.modules.scoring.service import score_intel_file
from app.modules.tracking_queries.service import generate_tracking_queries
from app.schemas.api import ApiError, ApiResponse
from app.schemas.archives import TrendArchiveListData
from app.schemas.collaboration import (
    IntelFileCollaborationData,
    IntelFileCollaborationUpdateRequest,
    IntelFileCommentCreateData,
    IntelFileCommentCreateRequest,
    IntelFileCommentListData,
)
from app.schemas.intel_files import (
    EvidenceAttachData,
    EvidenceAttachRequest,
    EvidenceSummary,
    IntelFileCreateData,
    IntelFileCreateRequest,
    IntelFileDetailData,
    IntelFileListData,
)
from app.schemas.lifecycle import (
    LifecycleEvaluateData,
    LifecycleEvaluateRequest,
    LifecycleStatusOverrideData,
    LifecycleStatusOverrideRequest,
)
from app.schemas.match_suggestions import MatchSuggestionListData
from app.schemas.scoring import ScoreUpdateData, ScoreUpdateRequest
from app.schemas.tracking_queries import TrackingQueryGenerateData, TrackingQueryGenerateRequest

router = APIRouter(prefix="/intel-files", tags=["intel-files"])


@router.post("", response_model=ApiResponse[IntelFileCreateData])
def create_intel_file_route(
    payload: IntelFileCreateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileCreateData] | JSONResponse:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        intel_file = create_intel_file(db, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except IntelFileError as exc:
        return JSONResponse(
            status_code=422,
            content=ApiResponse[IntelFileCreateData](
                success=False,
                data=None,
                error=ApiError(code="validation_error", message=str(exc)),
            ).model_dump(),
        )

    return ApiResponse(
        success=True,
        data=IntelFileCreateData(intel_file=to_intel_file_summary(intel_file)),
        error=None,
    )


@router.get("", response_model=ApiResponse[IntelFileListData])
def list_intel_files_route(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: LifecycleStatus | None = Query(None),
    q: str | None = Query(None, max_length=200),
    sort: str = Query("updated_at", pattern="^(updated_at|last_seen_at|first_seen_at|opportunity_score|heat_score|risk_score|evidence_count)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileListData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = list_intel_files(
        db,
        page=page,
        page_size=page_size,
        status=status,
        q=q,
        sort=sort,
        order=order,
        workspace_id=x_workspace_id,
    )
    return ApiResponse(success=True, data=data, error=None)


@router.get("/{intel_file_id}", response_model=ApiResponse[IntelFileDetailData])
def get_intel_file_route(
    intel_file_id: UUID,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileDetailData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = get_intel_file_detail(db, intel_file_id, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.post("/{intel_file_id}/evidence", response_model=ApiResponse[EvidenceAttachData])
def attach_evidence_route(
    intel_file_id: UUID,
    payload: EvidenceAttachRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[EvidenceAttachData] | JSONResponse:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        evidence, intel_file = attach_evidence(db, intel_file_id, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EvidenceConflictError as exc:
        return JSONResponse(
            status_code=409,
            content=ApiResponse[EvidenceAttachData](
                success=False,
                data=None,
                error=ApiError(code="conflict", message=str(exc)),
            ).model_dump(),
        )

    return ApiResponse(
        success=True,
        data=EvidenceAttachData(
            evidence=EvidenceSummary.model_validate(evidence),
            intel_file=to_intel_file_summary(intel_file),
        ),
        error=None,
    )


@router.post("/{intel_file_id}/evaluate", response_model=ApiResponse[LifecycleEvaluateData])
def evaluate_intel_file_route(
    intel_file_id: UUID,
    payload: LifecycleEvaluateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[LifecycleEvaluateData]:
    try:
        data = evaluate_intel_file(db, intel_file_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.post("/{intel_file_id}/status", response_model=ApiResponse[LifecycleStatusOverrideData])
def override_intel_file_status_route(
    intel_file_id: UUID,
    payload: LifecycleStatusOverrideRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[LifecycleStatusOverrideData]:
    try:
        data = override_intel_file_status(db, intel_file_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.post("/{intel_file_id}/score", response_model=ApiResponse[ScoreUpdateData])
def score_intel_file_route(
    intel_file_id: UUID,
    payload: ScoreUpdateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[ScoreUpdateData]:
    try:
        data = score_intel_file(db, intel_file_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.post("/{intel_file_id}/tracking-queries", response_model=ApiResponse[TrackingQueryGenerateData])
def generate_tracking_queries_route(
    intel_file_id: UUID,
    payload: TrackingQueryGenerateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[TrackingQueryGenerateData]:
    try:
        data = generate_tracking_queries(db, intel_file_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.get("/{intel_file_id}/match-suggestions", response_model=ApiResponse[MatchSuggestionListData])
def list_match_suggestions_route(
    intel_file_id: UUID,
    status: str | None = Query("open"),
    db: Session = Depends(get_db),
) -> ApiResponse[MatchSuggestionListData]:
    try:
        data = list_match_suggestions(db, intel_file_id, status=status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.get("/{intel_file_id}/trend", response_model=ApiResponse[TrendArchiveListData])
def list_trend_archive_snapshots_route(
    intel_file_id: UUID,
    db: Session = Depends(get_db),
) -> ApiResponse[TrendArchiveListData]:
    try:
        data = list_trend_archive_snapshots(db, intel_file_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.patch("/{intel_file_id}/collaboration", response_model=ApiResponse[IntelFileCollaborationData])
def update_intel_file_collaboration_route(
    intel_file_id: UUID,
    payload: IntelFileCollaborationUpdateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileCollaborationData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = update_intel_file_collaboration(db, intel_file_id, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.get("/{intel_file_id}/comments", response_model=ApiResponse[IntelFileCommentListData])
def list_intel_file_comments_route(
    intel_file_id: UUID,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileCommentListData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = list_intel_file_comments(db, intel_file_id, workspace_id=x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)


@router.post("/{intel_file_id}/comments", response_model=ApiResponse[IntelFileCommentCreateData])
def create_intel_file_comment_route(
    intel_file_id: UUID,
    payload: IntelFileCommentCreateRequest,
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[IntelFileCommentCreateData]:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = create_intel_file_comment(
            db,
            intel_file_id,
            payload,
            author_email=x_user_email,
            workspace_id=x_workspace_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApiResponse(success=True, data=data, error=None)
