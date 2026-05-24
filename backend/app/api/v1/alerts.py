from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

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
    db: Session = Depends(get_db),
) -> ApiResponse[AlertListData]:
    data = list_alerts(db, status=status, alert_type=alert_type, severity=severity)
    return ApiResponse(success=True, data=data, error=None)


@router.patch("/{alert_id}", response_model=ApiResponse[AlertSummary])
def patch_alert(
    alert_id: UUID,
    payload: AlertUpdateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AlertSummary] | JSONResponse:
    try:
        data = update_alert_status(db, alert_id, payload)
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
