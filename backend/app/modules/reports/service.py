from io import BytesIO
from typing import Iterable

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.schemas.briefings import BriefingItem, DailyBriefingData, WeeklyRetrospectiveData


def _item_lines(items: Iterable[BriefingItem]) -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(f"- {item.title} [{item.status.value}]: {item.reason}")
    return lines or ["- No items."]


def render_daily_markdown(data: DailyBriefingData) -> str:
    sections = [
        ("Resurrected Signals", data.sections.resurrected),
        ("High Opportunity", data.sections.high_opportunity),
        ("Risk / Noise", data.sections.risk_or_noise),
        ("New Intel Files", data.sections.new_files),
        ("Updated Intel Files", data.sections.updated_files),
    ]
    lines = ["# Daily Intelligence Briefing", "", data.overview, ""]
    for title, items in sections:
        lines.extend([f"## {title}", "", *_item_lines(items), ""])
    return "\n".join(lines)


def render_weekly_markdown(data: WeeklyRetrospectiveData) -> str:
    sections = [
        ("Changed Files", data.sections.changed_files),
        ("Resurrected Signals", data.sections.resurrected),
        ("Verified / Debunked", data.sections.verified_or_debunked),
        ("Opportunity Gainers", data.sections.opportunity_gainers),
        ("Cooling / Noise", data.sections.cooling_or_noise),
    ]
    lines = ["# Weekly Intelligence Retrospective", "", data.overview, ""]
    for title, items in sections:
        lines.extend([f"## {title}", "", *_item_lines(items), ""])
    return "\n".join(lines)


def render_pdf_bytes(markdown: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
            story.append(Spacer(1, 12))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
            story.append(Spacer(1, 8))
        elif line.startswith("- "):
            story.append(Paragraph(line, styles["BodyText"]))
        elif line.strip():
            story.append(Paragraph(line, styles["BodyText"]))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 6))
    doc.build(story)
    return buffer.getvalue()
