from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.alerts import router as alerts_router
from app.api.v1.archives import router as archives_router
from app.api.v1.auth import router as auth_router
from app.api.v1.briefings import router as briefings_router
from app.api.v1.extraction import router as extraction_router
from app.api.v1.health import HealthResponse, ReadinessResponse
from app.db.session import get_db
from app.api.v1.inbox import router as inbox_router
from app.api.v1.intel_files import router as intel_files_router
from app.api.v1.lifecycle import router as lifecycle_router
from app.api.v1.match_suggestions import router as match_suggestions_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.reports import router as reports_router
from app.api.v1.saved_views import router as saved_views_router
from app.api.v1.usage import router as usage_router
from app.api.v1.source_checks import router as source_checks_router

router = APIRouter()
router.include_router(inbox_router)
router.include_router(extraction_router)
router.include_router(intel_files_router)
router.include_router(alerts_router)
router.include_router(auth_router)
router.include_router(archives_router)
router.include_router(briefings_router)
router.include_router(source_checks_router)
router.include_router(lifecycle_router)
router.include_router(match_suggestions_router)
router.include_router(notifications_router)
router.include_router(reports_router)
router.include_router(saved_views_router)
router.include_router(usage_router)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    from app.core.config import get_settings

    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(db: Session = Depends(get_db)) -> ReadinessResponse:
    from app.core.config import get_settings

    settings = get_settings()
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is not ready.") from exc
    return ReadinessResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
        database="ok",
    )
