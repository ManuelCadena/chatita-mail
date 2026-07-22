"""
Chatita Mail v3.0 - Security routes (phishing analysis + quarantine).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.security import PhishingDetector
from backend.models.db import get_session
from backend.models.entities import Email, EmailStatus, SecurityEvent
from backend.models.schemas import SecurityResult

router = APIRouter(prefix="/api/security", tags=["security"])

_detector = PhishingDetector()


@router.post("/analyze", response_model=SecurityResult)
async def analyze_content(
    from_address: str,
    subject: str | None = None,
    body_text: str | None = None,
) -> SecurityResult:
    """Ad-hoc phishing analysis with XAI (no persistence)."""
    return await _detector.analyze(
        from_address=from_address, subject=subject, body_text=body_text
    )


@router.get("/events")
async def list_security_events(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """List recent security events, highest risk first."""
    stmt = (
        select(SecurityEvent)
        .order_by(SecurityEvent.risk_score.desc(), SecurityEvent.created_at.desc())
        .limit(min(limit, 200))
    )
    events = list((await session.scalars(stmt)).all())
    return [
        {
            "email_id": e.email_id,
            "risk_score": e.risk_score,
            "risk_level": e.risk_level,
            "event_type": e.event_type,
            "explanation": e.explanation,
            "recommended_action": e.recommended_action,
        }
        for e in events
    ]


@router.post("/{email_id}/release")
async def release_from_quarantine(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """Manually release a quarantined email back to the inbox (human override)."""
    email = await session.scalar(select(Email).where(Email.id == email_id))
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    if email.status not in (EmailStatus.QUARANTINED, EmailStatus.BLOCKED):
        raise HTTPException(status_code=400, detail="Email is not quarantined/blocked")
    email.status = EmailStatus.INBOX
    await session.flush()
    return {"email_id": email_id, "status": EmailStatus.INBOX}
