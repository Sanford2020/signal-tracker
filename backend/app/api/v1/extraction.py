from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import RawItem
from app.modules.extraction.normalize import ExtractionError
from app.modules.extraction.service import analyze_raw_item, to_analysis_read_dict
from app.modules.usage.service import UsageLimitError
from app.schemas.api import ApiError, ApiResponse
from app.schemas.extraction import AnalysisData, AnalyzeResponseData

router = APIRouter(tags=["extraction"])


@router.post("/raw-items/{raw_item_id}/analyze", response_model=ApiResponse[AnalyzeResponseData])
def analyze_raw_item_route(
    raw_item_id: UUID,
    db: Session = Depends(get_db),
) -> ApiResponse[AnalyzeResponseData] | JSONResponse:
    try:
        analysis = analyze_raw_item(db, raw_item_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ExtractionError as exc:
        return JSONResponse(
            status_code=422,
            content=ApiResponse[AnalyzeResponseData](
                success=False,
                data=None,
                error=ApiError(code="extraction_error", message=str(exc)),
            ).model_dump(),
        )
    except UsageLimitError as exc:
        return JSONResponse(
            status_code=429,
            content=ApiResponse[AnalyzeResponseData](
                success=False,
                data=None,
                error=ApiError(code="usage_limit_exceeded", message=str(exc)),
            ).model_dump(),
        )

    return ApiResponse(
        success=True,
        data=AnalyzeResponseData(analysis=AnalysisData.model_validate(to_analysis_read_dict(analysis))),
        error=None,
    )
