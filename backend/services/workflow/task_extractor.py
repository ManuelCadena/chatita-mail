"""
Chatita Mail v3.0 — Phase 2: Task & Commitment Extractor.

Given an email, delegates to AION Brain to extract:
  - tasks       : actionable items the USER must do (with optional deadline/type/priority)
  - commitments : promises made (by "me" or by the "sender") with a due date

The LLM is asked to return STRICT JSON. We parse defensively and persist to the
`tasks` and `commitments` tables. If AION Brain is unavailable, a light regex
fallback extracts obvious deadline phrases so the pipeline never blocks.

This is a Chatita Mail client concern — it only *calls* AION Brain (orchestrate),
it does NOT modify AION Brain itself.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from dateutil import parser as dateparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.aion_client import AIONBrainClient
from backend.models.entities import Commitment, Email, Task

logger = logging.getLogger("chatita_mail.workflow")

_MAX_BODY = 4000  # chars sent to the LLM (cost control)

_PROMPT = """You are an executive assistant. Read the email below and extract:
1. TASKS: concrete actions the RECIPIENT must take. Each task: a short imperative \
description, optional ISO-8601 deadline, type (calendar|document|reply|payment|reminder|other), \
priority (high|medium|low).
2. COMMITMENTS: explicit promises. who = "me" (recipient) or "sender"; what = the promise; \
optional ISO-8601 deadline.

Return ONLY valid minified JSON, no markdown, with this exact shape:
{{"tasks":[{{"description":"...","deadline":null,"task_type":"reply","priority":"medium"}}],\
"commitments":[{{"who":"me","what":"...","deadline":null}}]}}
If there are none, return {{"tasks":[],"commitments":[]}}.

Today is {today}.

FROM: {sender}
SUBJECT: {subject}
BODY:
{body}
"""


@dataclass
class ExtractionResult:
    tasks: list[dict] = field(default_factory=list)
    commitments: list[dict] = field(default_factory=list)
    source: str = "llm"  # llm | fallback | none


class TaskExtractor:
    def __init__(self, aion: AIONBrainClient | None = None) -> None:
        self.aion = aion or AIONBrainClient()

    # ── Public API ──────────────────────────────────────────
    async def extract(
        self,
        *,
        from_address: str,
        from_name: str | None,
        subject: str | None,
        body_text: str | None,
    ) -> ExtractionResult:
        body = (body_text or "").strip()[:_MAX_BODY]
        if not body and not subject:
            return ExtractionResult(source="none")

        prompt = _PROMPT.format(
            today=datetime.utcnow().date().isoformat(),
            sender=f"{from_name} <{from_address}>" if from_name else from_address,
            subject=subject or "(no subject)",
            body=body or "(empty)",
        )

        try:
            resp = await self.aion.orchestrate(prompt, task_type="medium", priority="P2")
            text = (resp or {}).get("text") or ""
            if not text or (resp or {}).get("fallback"):
                return self._fallback(subject, body)
            parsed = self._parse_json(text)
            if parsed is None:
                return self._fallback(subject, body)
            return ExtractionResult(
                tasks=self._clean_tasks(parsed.get("tasks", [])),
                commitments=self._clean_commitments(parsed.get("commitments", [])),
                source="llm",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("TaskExtractor LLM failed: %s", exc)
            return self._fallback(subject, body)

    async def extract_and_persist(
        self, session: AsyncSession, email: Email, *, replace: bool = True
    ) -> ExtractionResult:
        """Extract tasks/commitments for an email and upsert them."""
        result = await self.extract(
            from_address=email.from_address,
            from_name=email.from_name,
            subject=email.subject,
            body_text=email.body_text,
        )

        if replace:
            existing_tasks = (
                await session.scalars(select(Task).where(Task.email_id == email.id))
            ).all()
            for t in existing_tasks:
                await session.delete(t)
            existing_c = (
                await session.scalars(select(Commitment).where(Commitment.email_id == email.id))
            ).all()
            for c in existing_c:
                await session.delete(c)

        for t in result.tasks:
            session.add(
                Task(
                    email_id=email.id,
                    description=t["description"],
                    task_type=t.get("task_type"),
                    priority=t.get("priority"),
                    deadline=t.get("deadline"),
                    status="pending",
                )
            )
        for c in result.commitments:
            session.add(
                Commitment(
                    email_id=email.id,
                    who=c.get("who", "me")[:320],
                    what=c["what"],
                    deadline=c.get("deadline"),
                    status="pending",
                )
            )
        await session.flush()
        return result

    # ── Parsing helpers ─────────────────────────────────────
    @staticmethod
    def _parse_json(text: str) -> dict | None:
        text = text.strip()
        # Strip markdown fences if the model added them.
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
        # Grab the first {...} block.
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None

    def _clean_tasks(self, raw: list) -> list[dict]:
        out: list[dict] = []
        for item in raw or []:
            if not isinstance(item, dict):
                continue
            desc = (item.get("description") or "").strip()
            if not desc:
                continue
            out.append(
                {
                    "description": desc[:500],
                    "task_type": self._norm(item.get("task_type")),
                    "priority": self._norm(item.get("priority")) or "medium",
                    "deadline": self._parse_date(item.get("deadline")),
                }
            )
        return out[:10]

    def _clean_commitments(self, raw: list) -> list[dict]:
        out: list[dict] = []
        for item in raw or []:
            if not isinstance(item, dict):
                continue
            what = (item.get("what") or "").strip()
            if not what:
                continue
            who = (item.get("who") or "me").strip().lower()
            who = who if who in ("me", "sender") else who[:320]
            out.append(
                {"who": who, "what": what[:500], "deadline": self._parse_date(item.get("deadline"))}
            )
        return out[:10]

    @staticmethod
    def _norm(v) -> str | None:
        if not v or not isinstance(v, str):
            return None
        return v.strip().lower()[:20] or None

    @staticmethod
    def _parse_date(v) -> datetime | None:
        if not v or not isinstance(v, str):
            return None
        try:
            return dateparser.parse(v)
        except (ValueError, OverflowError):
            return None

    # ── Fallback (offline) ──────────────────────────────────
    def _fallback(self, subject: str | None, body: str) -> ExtractionResult:
        """Very light heuristic: detect deadline words + imperative subject."""
        text = f"{subject or ''}\n{body}".lower()
        tasks: list[dict] = []
        deadline = None
        if re.search(r"\b(hoy|today|urgent|urgente|asap|end of day|eod)\b", text):
            deadline = datetime.utcnow().replace(hour=23, minute=59, second=0, microsecond=0)
        elif re.search(r"\b(ma[nñ]ana|tomorrow)\b", text):
            deadline = (datetime.utcnow() + timedelta(days=1)).replace(
                hour=17, minute=0, second=0, microsecond=0
            )
        if subject and re.search(
            r"\b(review|revisa|sign|firma|pay|paga|send|env[ií]a|confirm|schedule|agenda)\b",
            subject.lower(),
        ):
            tasks.append(
                {
                    "description": subject.strip()[:500],
                    "task_type": "reply",
                    "priority": "high" if deadline else "medium",
                    "deadline": deadline,
                }
            )
        return ExtractionResult(tasks=tasks, commitments=[], source="fallback")
