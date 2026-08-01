"""
Chatita Mail v3.0 — Phase 2: Tasks & Commitments routes.

Surfaces AION-extracted actionable items so the user can act in <=5 min/day:
  GET   /api/tasks                    -> open tasks across the mailbox
  GET   /api/commitments              -> open commitments
  POST  /api/inbox/emails/{id}/extract-> (re)run extraction for one email
  PATCH /api/tasks/{id}               -> update task status (done|dismissed|pending)
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.db import get_session
from backend.models.entities import Commitment, Email, Task
from backend.models.schemas import CommitmentOut, TaskOut, TaskStatusIn
from backend.services.workflow import Composer, StyleLearningEngine, TaskExtractor
from backend.services.workflow.composer import detect_language
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["workflow"])

_extractor = TaskExtractor()
_composer = Composer()
_style = StyleLearningEngine()


def _email_lang(email) -> str:
    """Detected language of an email (subject + body), shared by draft routes."""
    text = f"{email.subject or ''}\n{email.body_text or email.snippet or ''}"
    return detect_language(text)


class DraftReplyIn(BaseModel):
    tone: str = "professional"
    instructions: str | None = None


@router.get("/tasks", response_model=list[TaskOut])
async def list_tasks(
    status: str | None = Query(None, description="pending | done | dismissed"),
    limit: int = Query(100, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[TaskOut]:
    stmt = select(Task).order_by(
        Task.deadline.asc().nullslast(), Task.created_at.desc()
    ).limit(limit)
    if status:
        stmt = stmt.where(Task.status == status)
    rows = (await session.scalars(stmt)).all()
    return [TaskOut.model_validate(t) for t in rows]


@router.get("/commitments", response_model=list[CommitmentOut])
async def list_commitments(
    status: str | None = Query(None),
    limit: int = Query(100, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[CommitmentOut]:
    stmt = select(Commitment).order_by(
        Commitment.deadline.asc().nullslast(), Commitment.created_at.desc()
    ).limit(limit)
    if status:
        stmt = stmt.where(Commitment.status == status)
    rows = (await session.scalars(stmt)).all()
    return [CommitmentOut.model_validate(c) for c in rows]


@router.get("/inbox/emails/{email_id}/tasks")
async def email_tasks(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    tasks = (
        await session.scalars(select(Task).where(Task.email_id == email_id))
    ).all()
    commits = (
        await session.scalars(select(Commitment).where(Commitment.email_id == email_id))
    ).all()
    return {
        "tasks": [TaskOut.model_validate(t).model_dump() for t in tasks],
        "commitments": [CommitmentOut.model_validate(c).model_dump() for c in commits],
    }


@router.post("/inbox/emails/{email_id}/extract")
async def extract_email(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """(Re)run task/commitment extraction for a single email."""
    email = await session.scalar(select(Email).where(Email.id == email_id))
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    result = await _extractor.extract_and_persist(session, email, replace=True)
    return {
        "email_id": email_id,
        "source": result.source,
        "tasks_extracted": len(result.tasks),
        "commitments_extracted": len(result.commitments),
        "tasks": result.tasks,
        "commitments": result.commitments,
    }


@router.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str, payload: TaskStatusIn, session: AsyncSession = Depends(get_session)
) -> TaskOut:
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = payload.status
    await session.flush()
    return TaskOut.model_validate(task)


@router.patch("/commitments/{commitment_id}", response_model=CommitmentOut)
async def update_commitment(
    commitment_id: str, payload: TaskStatusIn, session: AsyncSession = Depends(get_session)
) -> CommitmentOut:
    c = await session.scalar(select(Commitment).where(Commitment.id == commitment_id))
    if not c:
        raise HTTPException(status_code=404, detail="Commitment not found")
    c.status = payload.status
    await session.flush()
    return CommitmentOut.model_validate(c)


# ── Phase 2: Composer (AION Brain) ──────────────────────────
async def _load_email(session: AsyncSession, email_id: str) -> Email:
    email = await session.scalar(select(Email).where(Email.id == email_id))
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/inbox/emails/{email_id}/summarize")
async def summarize_email(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """AI TL;DR + key points + suggested action for one email."""
    email = await _load_email(session, email_id)
    r = await _composer.summarize_email(email)
    return {
        "email_id": email_id,
        "tldr": r.tldr,
        "key_points": r.key_points,
        "suggested_action": r.suggested_action,
        "requires_reply": r.requires_reply,
        "source": r.source,
    }


@router.post("/inbox/emails/{email_id}/draft-reply")
async def draft_reply(
    email_id: str,
    payload: DraftReplyIn | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Generate an editable reply draft in Manny's learned voice."""
    email = await _load_email(session, email_id)
    payload = payload or DraftReplyIn()
    # Personalize with the learned style profile if one exists (Phase 3 / T3.1),
    # adapting language-bound cues to the email's detected language (T3.5).
    sp = await _style.get_profile(session)
    directive = _style.directive(sp.profile, target_lang=_email_lang(email)) if sp else None
    r = await _composer.draft_reply(
        email,
        tone=payload.tone,
        instructions=payload.instructions,
        style_directive=directive,
    )
    return {
        "email_id": email_id,
        "subject": r.subject,
        "body": r.body,
        "tone": r.tone,
        "source": r.source,
        "language": r.language,
        "style_applied": bool(directive),
        "style_samples": sp.sample_size if sp else 0,
    }


@router.post("/inbox/emails/{email_id}/draft-variants")
async def draft_variants(
    email_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    """T3.2 — three styled reply options (Natural/Profesional/Breve) + XAI 'why'."""
    email = await _load_email(session, email_id)
    sp = await _style.get_profile(session)
    directive = _style.directive(sp.profile, target_lang=_email_lang(email)) if sp else None
    result = await _composer.draft_variants(email, style_directive=directive)
    return {
        "email_id": email_id,
        **result,
        "style_applied": bool(directive),
        "style_samples": sp.sample_size if sp else 0,
    }


# ── Phase 3 (T3.1): Style learning ──────────────────────────
@router.post("/inbox/style/learn")
async def learn_style(
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Analyze SENT emails and (re)build Manny's writing-style profile."""
    row = await _style.learn(session, limit=limit)
    return {
        "user_key": row.user_key,
        "sample_size": row.sample_size,
        "profile": row.profile,
    }


class StyleFeedbackIn(BaseModel):
    final_body: str
    ai_body: str | None = None
    style: str | None = None
    email_id: str | None = None


@router.post("/inbox/style/feedback")
async def style_feedback(
    payload: StyleFeedbackIn, session: AsyncSession = Depends(get_session)
) -> dict:
    """T3.3 — record how Manny edited an AI draft before sending; adapt profile."""
    return await _style.record_feedback(
        session,
        final_body=payload.final_body,
        ai_body=payload.ai_body,
        style=payload.style,
        email_id=payload.email_id,
    )


@router.get("/inbox/style/metrics")
async def style_metrics(session: AsyncSession = Depends(get_session)) -> dict:
    """T3.3/T3.4 — acceptance metrics (trust score inputs)."""
    return await _style.edit_rate(session)


# ── Phase 4 (T4.2): Google Drive attachment suggestions ─────
@router.get("/inbox/drive/search")
async def drive_search(
    q: str = Query("", description="Full-text query"),
    limit: int = Query(8, ge=1, le=25),
) -> dict:
    """T4.2 — suggest Drive files to attach (read-only). Runs off the event loop."""
    import asyncio

    from backend.services.email.drive_connector import DriveConnector

    conn = DriveConnector()
    if not conn.enabled():
        return {"enabled": False, "files": []}
    try:
        files = await asyncio.to_thread(conn.search, q, limit)
        return {"enabled": True, "files": files}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Drive error: {str(exc)[:200]}") from exc


# ── Phase 4 (T4.1): Voice replies via ElevenLabs TTS ────────
class TTSIn(BaseModel):
    text: str
    voice_id: str | None = None


@router.get("/voice/health")
async def voice_health() -> dict:
    """Report whether the voice (TTS) feature is configured."""
    return {
        "enabled": bool(settings.elevenlabs_api_key and settings.elevenlabs_voice_id),
        "voice_id": settings.elevenlabs_voice_id or None,
        "model": settings.elevenlabs_model_id,
    }


@router.post("/voice/tts")
async def voice_tts(payload: TTSIn) -> Response:
    """T4.1 — synthesize reply text to speech (returns audio/mpeg)."""
    if not (settings.elevenlabs_api_key and settings.elevenlabs_voice_id):
        raise HTTPException(status_code=503, detail="Voice not configured")
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")
    text = text[:5000]  # ElevenLabs per-request cap
    voice_id = payload.voice_id or settings.elevenlabs_voice_id
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": settings.elevenlabs_model_id,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=body, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"TTS upstream error: {exc}") from exc
    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"ElevenLabs {resp.status_code}: {resp.text[:200]}",
        )
    return Response(
        content=resp.content,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )


@router.get("/inbox/style")
async def get_style(session: AsyncSession = Depends(get_session)) -> dict:
    """Return the current learned style profile (or an empty shell if none)."""
    row = await _style.get_profile(session)
    if row is None:
        return {"user_key": _style.default_user_key(), "sample_size": 0, "profile": None}
    return {
        "user_key": row.user_key,
        "sample_size": row.sample_size,
        "profile": row.profile,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }
