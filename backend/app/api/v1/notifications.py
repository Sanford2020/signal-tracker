from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_workspace_access
from app.db.session import get_db
from app.modules.notifications.service import (
    create_notification_channel,
    list_notification_channels,
    run_notification_delivery,
)
from app.schemas.api import ApiResponse
from app.schemas.notifications import (
    NotificationChannelCreateData,
    NotificationChannelCreateRequest,
    NotificationChannelListData,
    NotificationDeliveryRunData,
    NotificationDeliveryRunRequest,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/channels", response_model=ApiResponse[NotificationChannelCreateData])
def create_notification_channel_route(
    payload: NotificationChannelCreateRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationChannelCreateData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = create_notification_channel(db, payload, workspace_id=x_workspace_id)
    return ApiResponse(success=True, data=data, error=None)


@router.get("/channels", response_model=ApiResponse[NotificationChannelListData])
def list_notification_channels_route(
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationChannelListData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = list_notification_channels(db, workspace_id=x_workspace_id)
    return ApiResponse(success=True, data=data, error=None)


@router.post("/deliveries/run", response_model=ApiResponse[NotificationDeliveryRunData])
def run_notification_delivery_route(
    payload: NotificationDeliveryRunRequest,
    x_workspace_id: UUID | None = Header(None, alias="X-Workspace-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
    x_user_token: str | None = Header(None, alias="X-User-Token"),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationDeliveryRunData]:
    require_workspace_access(db, x_workspace_id, x_user_email, x_user_token)
    data = run_notification_delivery(db, payload, workspace_id=x_workspace_id)
    return ApiResponse(success=True, data=data, error=None)
