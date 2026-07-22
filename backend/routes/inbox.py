"""
Chatita Mail v3.0 - Inbox routes.

Endpoints to ingest, list, and read emails.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.db import get_session
from backend.models.entities import (
    AccountProvider,
    Email,
    EmailAccount,
    EmailCategory,
    EmailStatus,
)
from backend.models.schemas import EmailIn, EmailOut

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


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
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[EmailOut]:
    """List emails with optional status/category filters, newest first."""
    stmt = (
        select(Email)
        .options(selectinload(Email.classification), selectinload(Email.security_event))
        .order_by(Email.received_at.desc().nullslast(), Email.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status:
        stmt = stmt.where(Email.status == status)

    emails = list((await session.scalars(stmt)).all())

    out: list[EmailOut] = []
    for e in emails:
        if category and (not e.classification or e.classification.category != category):
            continue
        item = EmailOut.model_validate(e)
        if e.classification:
            item.category = e.classification.category
            item.confidence = e.classification.confidence
        if e.security_event:
            item.risk_level = e.security_event.risk_level
            item.risk_score = e.security_event.risk_score
        out.append(item)
    return out


@router.get("/emails/{email_id}")
async def get_email(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """Full email detail including classification + security XAI."""
    email = await session.scalar(
        select(Email)
        .options(selectinload(Email.classification), selectinload(Email.security_event))
        .where(Email.id == email_id)
    )
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return {
        "id": email.id,
        "from_address": email.from_address,
        "from_name": email.from_name,
        "subject": email.subject,
        "body_text": email.body_text,
        "status": email.status,
        "received_at": email.received_at,
        "classification": {
            "category": email.classification.category,
            "confidence": email.classification.confidence,
            "stage": email.classification.stage,
            "reasoning": email.classification.reasoning,
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
    }
