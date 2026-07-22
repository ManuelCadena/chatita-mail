"""
Chatita Mail v3.0 - Classification & triage routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db import get_session
from backend.models.entities import Classification, Email
from backend.models.schemas import ClassificationResult, ReclassifyIn
from backend.services.triage import TriageService

router = APIRouter(prefix="/api/classify", tags=["classify"])

_triage = TriageService()


# NOTE: Static routes (/preview) MUST be declared before the dynamic
# /{email_id} route, otherwise FastAPI captures "preview" as email_id.
@router.post("/preview", response_model=ClassificationResult)
async def classify_preview(
    from_address: str,
    subject: str | None = None,
    body_text: str | None = None,
) -> ClassificationResult:
    """Classify ad-hoc content without persisting (useful for testing/tuning)."""
    return await _triage.classifier.classify(
        from_address=from_address, subject=subject, body_text=body_text
    )


@router.post("/{email_id}")
async def triage_email(
    email_id: str,
    auto_actions: bool = True,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Run full triage (classification + security + actions) on a stored email."""
    email = await session.scalar(select(Email).where(Email.id == email_id))
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    outcome = await _triage.triage_email(session, email, auto_actions=auto_actions)
    return {
        "email_id": outcome.email_id,
        "category": outcome.category,
        "confidence": outcome.confidence,
        "stage": outcome.stage,
        "risk_level": outcome.risk_level,
        "risk_score": outcome.risk_score,
        "status": outcome.status,
        "actions": outcome.actions,
    }


@router.patch("/{email_id}/reclassify")
async def reclassify(
    email_id: str,
    payload: ReclassifyIn,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Human correction (active learning against temporal drift, Asliyuksek 2025).
    Stored for future feedback-loop retraining.
    """
    from datetime import datetime, timezone

    cls = await session.scalar(
        select(Classification).where(Classification.email_id == email_id)
    )
    if not cls:
        raise HTTPException(status_code=404, detail="Classification not found")

    cls.user_corrected_category = payload.category
    cls.corrected_at = datetime.now(timezone.utc)
    await session.flush()
    return {"email_id": email_id, "corrected_category": payload.category}
