import hashlib
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import RawItem, Source, SourceType
from app.modules.intel_files.service import raw_item_ids_with_intel_file
from app.schemas.inbox import InboxListData, InboxListItem, InboxRawItem, InboxSubmitData, InboxSubmitRequest

MANUAL_SOURCE_NAME = "Manual Intake"


def compute_content_hash(url: str | None, content: str | None, title: str | None = None) -> str:
    parts: list[str] = []
    if url and url.strip():
        parts.append(f"url:{url.strip().lower()}")
    if content and content.strip():
        parts.append(f"content:{content.strip()}")
    if not parts and title and title.strip():
        parts.append(f"title:{title.strip()}")
    normalized = "|".join(parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def resolve_title(url: str | None, title: str | None, content: str | None) -> str:
    if title and title.strip():
        return title.strip()
    if url and url.strip():
        return url.strip()
    if content and content.strip():
        snippet = content.strip().splitlines()[0]
        return snippet[:120] if len(snippet) > 120 else snippet
    return "Untitled signal"


def get_or_create_manual_source(db: Session) -> Source:
    source = db.scalar(
        select(Source).where(
            Source.source_type == SourceType.MANUAL,
            Source.name == MANUAL_SOURCE_NAME,
        )
    )
    if source:
        return source

    source = Source(
        name=MANUAL_SOURCE_NAME,
        source_type=SourceType.MANUAL,
        trust_tier=2,
        enabled=True,
    )
    db.add(source)
    db.flush()
    return source


def resolve_source(db: Session, source_id: UUID | None) -> Source:
    if source_id:
        source = db.get(Source, source_id)
        if source is None:
            raise ValueError("Source not found.")
        return source
    return get_or_create_manual_source(db)


def to_inbox_raw_item(raw_item: RawItem) -> InboxRawItem:
    return InboxRawItem(
        id=raw_item.id,
        workspace_id=raw_item.workspace_id,
        title=raw_item.title,
        url=raw_item.url,
        content=raw_item.content,
        source_id=raw_item.source_id,
        content_hash=raw_item.content_hash,
        published_at=raw_item.published_at,
        captured_at=raw_item.captured_at,
    )


def submit_inbox_item(
    db: Session,
    payload: InboxSubmitRequest,
    *,
    workspace_id: UUID | None = None,
) -> InboxSubmitData:
    content_hash = compute_content_hash(payload.url, payload.content, payload.title)
    existing = db.scalar(select(RawItem).where(RawItem.content_hash == content_hash))
    if existing:
        return InboxSubmitData(raw_item=to_inbox_raw_item(existing), duplicate=True)

    source = resolve_source(db, payload.source_id)
    raw_item = RawItem(
        source_id=source.id,
        workspace_id=workspace_id,
        title=resolve_title(payload.url, payload.title, payload.content),
        url=payload.url.strip() if payload.url and payload.url.strip() else None,
        content=payload.content.strip() if payload.content and payload.content.strip() else None,
        content_hash=content_hash,
    )
    db.add(raw_item)
    db.commit()
    db.refresh(raw_item)
    return InboxSubmitData(raw_item=to_inbox_raw_item(raw_item), duplicate=False)


def list_inbox_items(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    has_analysis: bool | None = None,
    workspace_id: UUID | None = None,
) -> InboxListData:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    query = select(RawItem).options(selectinload(RawItem.signal_analysis))
    count_query = select(func.count()).select_from(RawItem)

    if has_analysis is True:
        query = query.where(RawItem.signal_analysis.has())
        count_query = count_query.where(RawItem.signal_analysis.has())
    elif has_analysis is False:
        query = query.where(~RawItem.signal_analysis.has())
        count_query = count_query.where(~RawItem.signal_analysis.has())
    if workspace_id is not None:
        query = query.where(RawItem.workspace_id == workspace_id)
        count_query = count_query.where(RawItem.workspace_id == workspace_id)

    total = db.scalar(count_query) or 0
    items = db.scalars(
        query.order_by(RawItem.captured_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    promoted_ids = raw_item_ids_with_intel_file(db, [item.id for item in items])

    return InboxListData(
        items=[
            InboxListItem(
                raw_item=to_inbox_raw_item(item),
                analysis_status="complete" if item.signal_analysis else "pending",
                has_intel_file=item.id in promoted_ids,
            )
            for item in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
