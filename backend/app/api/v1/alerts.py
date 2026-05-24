from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.models.enums import AlertSeverity, AlertStatus, AlertType
from app.modules.alerts.service import list_alerts, update_alert_status
from app.schemas.alerts import AlertListData, AlertSummary, AlertUpdateRequest
from app.schemas.api import ApiError, ApiResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=ApiResponse[AlertListData])
def get_alerts(
    status: AlertStatus | None = Query(None),
    alert_type: AlertType | None = Query(None),
    severity: AlertSeverity | None = Query(None),
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[AlertListData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = list_alerts(
        db,
        status=status,
        alert_type=alert_type,
        severity=severity,
        workspace_id=x_workspace_id,
    )
    return ApiResponse(success=True, data=data, error=None)


@router.patch("/{alert_id}", response_model=ApiResponse[AlertSummary])
def patch_alert(
    alert_id: UUID,
    payload: AlertUpdateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[AlertSummary] | JSONResponse:
    try:
        require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
        data = update_alert_status(db, alert_id, payload, workspace_id=x_workspace_id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse(
            status_code=422,
            content=ApiResponse[AlertSummary](
                success=False,
                data=None,
                error=ApiError(code="validation_error", message=str(exc)),
            ).model_dump(),
        )
    return ApiResponse(success=True, data=data, error=None)
