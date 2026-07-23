"""
Chatita Mail v3.0 - Inbox routes.

Endpoints to ingest, list, and read emails.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.db import get_session
from backend.models.entities import (
    AccountProvider,
    Classification,
    Commitment,
    Email,
    EmailAccount,
    EmailCategory,
    EmailStatus,
    Task,
)
from backend.models.schemas import (
    CommitmentOut,
    EmailIn,
    EmailOut,
    InboxStats,
    ReadUpdateIn,
    StatusUpdateIn,
    TaskOut,
)
from backend.services.email.gmail_connector import GmailConnector
from backend.services.email.sync import GmailSyncService
from backend.services.unsubscribe import Unsubscriber

router = APIRouter(prefix="/api/inbox", tags=["inbox"])

_gmail_sync = GmailSyncService()
_unsubscriber = Unsubscriber()

# Minutes of manual triage saved per auto-handled email (archived/blocked/quarantined).
_MINUTES_SAVED_PER_EMAIL = 1.5


async def _get_or_create_account(session: AsyncSession, email_address: str) -> EmailAccount:
    account = await session.scalar(
        select(EmailAccount).where(EmailAccount.email_address == email_address)
    )
    if account:
        return account
    account = EmailAccount(
        provider=AccountProvider.IMAP,
        email_address=email_address,
        display_name=email_address,
    )
    session.add(account)
    await session.flush()
    return account


@router.post("/ingest", response_model=EmailOut, status_code=201)
async def ingest_email(
    payload: EmailIn,
    account_email: str = Query(..., description="Owner mailbox address"),
    session: AsyncSession = Depends(get_session),
) -> EmailOut:
    """Ingest a single email into the unified store (idempotent by provider id)."""
    account = await _get_or_create_account(session, account_email)

    existing = await session.scalar(
        select(Email).where(
            Email.account_id == account.id,
            Email.provider_message_id == payload.provider_message_id,
        )
    )
    if existing:
        return EmailOut.model_validate(existing)

    email = Email(
        account_id=account.id,
        provider_message_id=payload.provider_message_id,
        thread_id=payload.thread_id,
        from_address=payload.from_address,
        from_name=payload.from_name,
        to_addresses=payload.to_addresses,
        cc_addresses=payload.cc_addresses,
        subject=payload.subject,
        body_text=payload.body_text,
        body_html=payload.body_html,
        snippet=payload.snippet or (payload.body_text or "")[:200],
        attachments=payload.attachments,
        received_at=payload.received_at,
    )
    session.add(email)
    await session.flush()
    return EmailOut.model_validate(email)


@router.get("/emails", response_model=list[EmailOut])
async def list_emails(
    status: EmailStatus | None = Query(None),
    category: EmailCategory | None = Query(None),
    unread_only: bool = Query(False),
    search: str | None = Query(None, description="Match subject/sender/snippet"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[EmailOut]:
    """List emails with optional status/category/search filters, newest first."""
    stmt = (
        select(Email)
        .options(selectinload(Email.classification), selectinload(Email.security_event))
        .order_by(Email.received_at.desc().nullslast(), Email.created_at.desc())
    )
    if status:
        stmt = stmt.where(Email.status == status)
    if unread_only:
        stmt = stmt.where(Email.is_read.is_(False))
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Email.subject.ilike(like),
                Email.from_address.ilike(like),
                Email.from_name.ilike(like),
                Email.snippet.ilike(like),
            )
        )
    if category:
        stmt = stmt.join(Email.classification).where(Classification.category == category)

    stmt = stmt.limit(limit).offset(offset)
    emails = list((await session.scalars(stmt)).all())

    out: list[EmailOut] = []
    for e in emails:
        item = EmailOut.model_validate(e)
        item.has_html = bool(e.body_html)
        item.has_attachments = bool(e.attachments)
        if e.classification:
            item.category = e.classification.category
            item.confidence = e.classification.confidence
            item.is_newsletter = e.classification.is_newsletter
            item.unsubscribe_url = e.classification.unsubscribe_url
        if e.security_event:
            item.risk_level = e.security_event.risk_level
            item.risk_score = e.security_event.risk_score
        out.append(item)
    return out


@router.get("/stats", response_model=InboxStats)
async def inbox_stats(session: AsyncSession = Depends(get_session)) -> InboxStats:
    """Aggregate counts powering the sidebar (folders, categories, workload)."""
    total = await session.scalar(select(func.count(Email.id))) or 0
    unread = (
        await session.scalar(
            select(func.count(Email.id)).where(
                Email.is_read.is_(False), Email.status == EmailStatus.INBOX
            )
        )
        or 0
    )

    by_status: dict[str, int] = {}
    for st, cnt in (
        await session.execute(select(Email.status, func.count(Email.id)).group_by(Email.status))
    ).all():
        by_status[st.value if hasattr(st, "value") else str(st)] = cnt

    by_category: dict[str, int] = {}
    for cat, cnt in (
        await session.execute(
            select(Classification.category, func.count(Classification.id)).group_by(
                Classification.category
            )
        )
    ).all():
        by_category[cat.value if hasattr(cat, "value") else str(cat)] = cnt

    open_tasks = (
        await session.scalar(select(func.count(Task.id)).where(Task.status == "pending")) or 0
    )
    open_commitments = (
        await session.scalar(
            select(func.count(Commitment.id)).where(Commitment.status == "pending")
        )
        or 0
    )

    auto_handled = sum(
        by_status.get(s, 0)
        for s in ("ARCHIVED", "BLOCKED", "QUARANTINED")
    )
    time_saved = int(auto_handled * _MINUTES_SAVED_PER_EMAIL)

    return InboxStats(
        total=total,
        unread=unread,
        by_status=by_status,
        by_category=by_category,
        open_tasks=open_tasks,
        open_commitments=open_commitments,
        time_saved_minutes=time_saved,
    )


@router.get("/emails/{email_id}")
async def get_email(
    email_id: str,
    mark_read: bool = Query(True, description="Mark email as read when opened"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Full email detail including body (HTML+text), recipients, attachments,
    classification + security XAI, and Phase-2 tasks/commitments."""
    email = await session.scalar(
        select(Email)
        .options(selectinload(Email.classification), selectinload(Email.security_event))
        .where(Email.id == email_id)
    )
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if mark_read and not email.is_read:
        email.is_read = True
        await session.flush()

    tasks = (await session.scalars(select(Task).where(Task.email_id == email_id))).all()
    commits = (
        await session.scalars(select(Commitment).where(Commitment.email_id == email_id))
    ).all()

    return {
        "id": email.id,
        "from_address": email.from_address,
        "from_name": email.from_name,
        "to_addresses": email.to_addresses or [],
        "cc_addresses": email.cc_addresses or [],
        "subject": email.subject,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "snippet": email.snippet,
        "attachments": email.attachments or [],
        "status": email.status,
        "is_read": email.is_read,
        "thread_id": email.thread_id,
        "received_at": email.received_at,
        "classification": {
            "category": email.classification.category,
            "confidence": email.classification.confidence,
            "stage": email.classification.stage,
            "reasoning": email.classification.reasoning,
            "is_newsletter": email.classification.is_newsletter,
            "unsubscribe_url": email.classification.unsubscribe_url,
        }
        if email.classification
        else None,
        "security": {
            "risk_score": email.security_event.risk_score,
            "risk_level": email.security_event.risk_level,
            "explanation": email.security_event.explanation,
            "risk_factors": email.security_event.risk_factors,
            "recommended_action": email.security_event.recommended_action,
        }
        if email.security_event
        else None,
        "tasks": [TaskOut.model_validate(t).model_dump() for t in tasks],
        "commitments": [CommitmentOut.model_validate(c).model_dump() for c in commits],
    }


# ── Actions (mutations for the UI toolbar) ──────────────────
@router.patch("/emails/{email_id}/status", response_model=EmailOut)
async def update_status(
    email_id: str, payload: StatusUpdateIn, session: AsyncSession = Depends(get_session)
) -> EmailOut:
    """Move an email between folders (INBOX/ARCHIVED/DELETED/QUARANTINED...)."""
    email = await session.scalar(
        select(Email)
        .options(selectinload(Email.classification), selectinload(Email.security_event))
        .where(Email.id == email_id)
    )
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.status = payload.status
    await session.flush()
    return _to_out(email)


@router.patch("/emails/{email_id}/read", response_model=EmailOut)
async def update_read(
    email_id: str, payload: ReadUpdateIn, session: AsyncSession = Depends(get_session)
) -> EmailOut:
    email = await session.scalar(
        select(Email)
        .options(selectinload(Email.classification), selectinload(Email.security_event))
        .where(Email.id == email_id)
    )
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    email.is_read = payload.is_read
    await session.flush()
    return _to_out(email)


@router.post("/emails/{email_id}/unsubscribe")
async def unsubscribe_email(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """Attempt RFC-8058 one-click unsubscribe using the stored unsubscribe URL."""
    email = await session.scalar(
        select(Email).options(selectinload(Email.classification)).where(Email.id == email_id)
    )
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    url = email.classification.unsubscribe_url if email.classification else None
    if not url:
        raise HTTPException(status_code=400, detail="No unsubscribe URL for this email")
    result = await _unsubscriber.unsubscribe(url)
    if result.get("ok"):
        email.status = EmailStatus.ARCHIVED
        await session.flush()
    return result


def _to_out(email: Email) -> EmailOut:
    item = EmailOut.model_validate(email)
    item.has_html = bool(email.body_html)
    item.has_attachments = bool(email.attachments)
    if email.classification:
        item.category = email.classification.category
        item.confidence = email.classification.confidence
        item.is_newsletter = email.classification.is_newsletter
        item.unsubscribe_url = email.classification.unsubscribe_url
    if email.security_event:
        item.risk_level = email.security_event.risk_level
        item.risk_score = email.security_event.risk_score
    return item


@router.get("/gmail/health", tags=["gmail"])
async def gmail_health() -> dict:
    """Verify Gmail service-account delegation works for the configured mailbox."""
    return GmailConnector().health()


@router.post("/sync/gmail", tags=["gmail"])
async def sync_gmail(
    max_results: int = Query(10, le=50, description="How many recent INBOX emails to pull"),
    unread_only: bool = Query(False),
    triage: bool = Query(True, description="Run classification + security + auto-actions"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Pull recent Gmail emails, persist them, and (optionally) run the full
    triage pipeline. Idempotent by provider_message_id.
    """
    return await _gmail_sync.sync(
        session, max_results=max_results, unread_only=unread_only, run_triage=triage
    )
