"""
Chatita Mail v3.0 — Phase 2: Tasks & Commitments routes.

Surfaces AION-extracted actionable items so the user can act in <=5 min/day:
  GET   /api/tasks                    -> open tasks across the mailbox
  GET   /api/commitments              -> open commitments
  POST  /api/inbox/emails/{id}/extract-> (re)run extraction for one email
  PATCH /api/tasks/{id}               -> update task status (done|dismissed|pending)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.db import get_session
from backend.models.entities import Commitment, Email, Task
from backend.models.schemas import CommitmentOut, TaskOut, TaskStatusIn
from backend.services.workflow import TaskExtractor

router = APIRouter(prefix="/api", tags=["workflow"])

_extractor = TaskExtractor()


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
