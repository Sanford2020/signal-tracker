from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.briefings.service import generate_daily_briefing, generate_weekly_retrospective
from app.modules.reports.service import (
    render_daily_markdown,
    render_pdf_bytes,
    render_weekly_markdown,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily.md")
def export_daily_markdown(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> Response:
    markdown = render_daily_markdown(generate_daily_briefing(db, hours=hours))
    return Response(markdown, media_type="text/markdown")


@router.get("/weekly.md")
def export_weekly_markdown(
    days: int = Query(7, ge=1, le=31),
    db: Session = Depends(get_db),
) -> Response:
    markdown = render_weekly_markdown(generate_weekly_retrospective(db, days=days))
    return Response(markdown, media_type="text/markdown")


@router.get("/daily.pdf")
def export_daily_pdf(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
) -> Response:
    markdown = render_daily_markdown(generate_daily_briefing(db, hours=hours))
    return Response(render_pdf_bytes(markdown), media_type="application/pdf")


@router.get("/weekly.pdf")
def export_weekly_pdf(
    days: int = Query(7, ge=1, le=31),
    db: Session = Depends(get_db),
) -> Response:
    markdown = render_weekly_markdown(generate_weekly_retrospective(db, days=days))
    return Response(render_pdf_bytes(markdown), media_type="application/pdf")
