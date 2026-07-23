"""
Chatita Mail v3.0 — Phase 2: Composer (summaries + reply drafts).

Delegates to AION Brain (orchestrate) to:
  - summarize_email : a 2-3 sentence TL;DR + key points + suggested next action
  - draft_reply     : a ready-to-edit reply in Manny's voice (tone-adjustable)

Pure client concern: it only *calls* AION Brain, never modifies it. If AION is
unavailable, returns a graceful fallback derived from the email text so the UI
never blocks.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from backend.ai.aion_client import AIONBrainClient
from backend.models.entities import Email

logger = logging.getLogger("chatita_mail.workflow")

_MAX_BODY = 5000  # chars sent to the LLM (cost control)

_SUMMARY_PROMPT = """You are Manny's executive assistant. Summarize the email below.
Return ONLY valid minified JSON, no markdown, with this exact shape:
{{"tldr":"2-3 sentence summary","key_points":["point 1","point 2"],\
"suggested_action":"one short next step","requires_reply":true}}

FROM: {sender}
SUBJECT: {subject}
BODY:
{body}
"""

_REPLY_PROMPT = """You are Manny (Manuel Cadena) writing a reply to the email below.
Write in first person, {tone} tone, concise and professional, matching the email's
language (Spanish or English). Do NOT invent facts or commitments not supported by
the thread. If the email needs information Manny must provide, use a clear placeholder
in [brackets].
{extra}
Return ONLY valid minified JSON, no markdown, with this exact shape:
{{"subject":"Re: ...","body":"the reply text","tone":"{tone}"}}

FROM: {sender}
SUBJECT: {subject}
BODY:
{body}
"""

_VALID_TONES = {"professional", "friendly", "brief", "formal", "warm"}


@dataclass
class SummaryResult:
    tldr: str = ""
    key_points: list[str] = field(default_factory=list)
    suggested_action: str = ""
    requires_reply: bool = False
    source: str = "llm"  # llm | fallback


@dataclass
class ReplyDraft:
    subject: str = ""
    body: str = ""
    tone: str = "professional"
    source: str = "llm"  # llm | fallback


def _parse_json_block(text: str) -> dict | None:
    """Extract the first JSON object from an LLM response, tolerating fences."""
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        candidate = brace.group(0) if brace else None
    if candidate is None:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


class Composer:
    def __init__(self, aion: AIONBrainClient | None = None) -> None:
        self.aion = aion or AIONBrainClient()

    @staticmethod
    def _body_for(email: Email) -> str:
        return (email.body_text or email.snippet or "")[:_MAX_BODY]

    async def summarize_email(self, email: Email) -> SummaryResult:
        prompt = _SUMMARY_PROMPT.format(
            sender=email.from_name or email.from_address,
            subject=email.subject or "(no subject)",
            body=self._body_for(email),
        )
        try:
            resp = await self.aion.orchestrate(prompt, task_type="medium", priority="P2")
            data = _parse_json_block(resp.get("text", "")) if resp.get("ok", True) else None
            if data:
                return SummaryResult(
                    tldr=str(data.get("tldr", "")).strip(),
                    key_points=[str(p) for p in (data.get("key_points") or [])][:6],
                    suggested_action=str(data.get("suggested_action", "")).strip(),
                    requires_reply=bool(data.get("requires_reply", False)),
                    source="llm",
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("summarize_email AION failed: %s", exc)
        return self._fallback_summary(email)

    async def draft_reply(
        self, email: Email, tone: str = "professional", instructions: str | None = None
    ) -> ReplyDraft:
        tone = tone if tone in _VALID_TONES else "professional"
        extra = f"Additional instruction from Manny: {instructions}" if instructions else ""
        prompt = _REPLY_PROMPT.format(
            tone=tone,
            extra=extra,
            sender=email.from_name or email.from_address,
            subject=email.subject or "(no subject)",
            body=self._body_for(email),
        )
        try:
            resp = await self.aion.orchestrate(prompt, task_type="medium", priority="P2")
            data = _parse_json_block(resp.get("text", "")) if resp.get("ok", True) else None
            if data and str(data.get("body", "")).strip():
                subj = str(data.get("subject") or "").strip()
                if not subj:
                    subj = self._re_subject(email.subject)
                return ReplyDraft(
                    subject=subj,
                    body=str(data["body"]).strip(),
                    tone=str(data.get("tone") or tone),
                    source="llm",
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("draft_reply AION failed: %s", exc)
        return self._fallback_reply(email, tone)

    # ── fallbacks ───────────────────────────────────────────
    @staticmethod
    def _re_subject(subject: str | None) -> str:
        s = subject or "(no subject)"
        return s if s.lower().startswith("re:") else f"Re: {s}"

    def _fallback_summary(self, email: Email) -> SummaryResult:
        text = (email.body_text or email.snippet or "").strip()
        first = re.split(r"(?<=[.!?])\s+", text)
        tldr = " ".join(first[:2])[:280] if first else (email.subject or "")
        return SummaryResult(
            tldr=tldr or "(no content)",
            key_points=[],
            suggested_action="Review manually — AI summary unavailable.",
            requires_reply=False,
            source="fallback",
        )

    def _fallback_reply(self, email: Email, tone: str) -> ReplyDraft:
        greeting = (email.from_name or "").split(" ")[0] if email.from_name else ""
        body = (
            f"Hola{(' ' + greeting) if greeting else ''},\n\n"
            "Gracias por tu mensaje. [Escribe aquí tu respuesta.]\n\n"
            "Saludos,\nManuel"
        )
        return ReplyDraft(
            subject=self._re_subject(email.subject),
            body=body,
            tone=tone,
            source="fallback",
        )
