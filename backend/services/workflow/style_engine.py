"""
Chatita Mail v3.0 — Phase 3 (T3.1): StyleLearningEngine.

Learns Manny's writing style from his OUTBOUND (status=SENT) emails and stores a
compact `style_profile` JSON in the `style_profiles` table. The profile is later
injected into reply drafts (composer) so generated text sounds like Manny.

Research basis: Novelo 2025 (personalized style transfer from a user's own
corpus). Pure client concern: delegates the extraction to AION Brain; if AION is
unavailable or there are no samples, returns a graceful default so the UI never
blocks.

Flow:
  collect_samples()  -> most-recent authored text from SENT emails (quotes stripped)
  learn()            -> AION extracts a style JSON -> upsert StyleProfile
  get_profile()      -> read the stored profile (dict) or None
  directive()        -> compact NL instruction string for the reply prompt
"""
from __future__ import annotations

import asyncio
import json
import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.aion_client import AIONBrainClient
from backend.config import settings
from backend.models.entities import Email, EmailStatus, StyleProfile

logger = logging.getLogger("chatita_mail.style")

_MAX_SAMPLE_CHARS = 1200   # per-email cap sent to the LLM
_MAX_TOTAL_CHARS = 12000   # overall cap across all samples (cost control)
_MIN_DB_SAMPLES = 8        # below this, seed from the Gmail "SENT" label
_GMAIL_SEED_MAX = 60       # how many SENT messages to pull when seeding

# Markers where a *quoted* original begins — everything after is NOT Manny's text.
_QUOTE_MARKERS = [
    re.compile(r"-{2,}\s*Forwarded message", re.IGNORECASE),
    re.compile(r"-{2,}\s*Original Message", re.IGNORECASE),
    re.compile(r"\nOn .{0,80}wrote:", re.IGNORECASE),
    re.compile(r"\nEl .{0,80}escribió:", re.IGNORECASE),
    re.compile(r"\nDe:\s", re.IGNORECASE),
    re.compile(r"\nFrom:\s", re.IGNORECASE),
]

_STYLE_PROMPT = """You are a writing-style analyst. Below are several emails WRITTEN BY \
Manuel Cadena ("Manny"). Infer his personal writing style. Ignore quoted/forwarded \
text. Return ONLY valid minified JSON, no markdown, with exactly this shape:
{{"language_primary":"es|en","formality":"formal|neutral|casual",\
"greeting":"his typical opening line","signoff":"his typical closing (with name)",\
"avg_email_length":"short|medium|long","emoji_usage":"none|rare|frequent",\
"tone_descriptors":["adjective","adjective"],"common_phrases":["phrase","phrase"],\
"bullet_preference":true}}

EMAILS:
{samples}
"""

_DEFAULT_PROFILE = {
    "language_primary": "es",
    "formality": "neutral",
    "greeting": "Hola [nombre],",
    "signoff": "Saludos,\nManuel",
    "avg_email_length": "medium",
    "emoji_usage": "none",
    "tone_descriptors": ["directo", "profesional"],
    "common_phrases": [],
    "bullet_preference": False,
    "source": "default",
}


def _authored_text(body: str | None) -> str:
    """Return only the text Manny authored, cutting quoted/forwarded originals."""
    text = (body or "").strip()
    if not text:
        return ""
    cut = len(text)
    for rx in _QUOTE_MARKERS:
        m = rx.search(text)
        if m and m.start() < cut:
            cut = m.start()
    authored = text[:cut]
    # Drop trailing quoted lines (leading '>') just in case.
    lines = [ln for ln in authored.splitlines() if not ln.lstrip().startswith(">")]
    return "\n".join(lines).strip()[:_MAX_SAMPLE_CHARS]


def _parse_json_block(text: str) -> dict | None:
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


class StyleLearningEngine:
    def __init__(self, aion: AIONBrainClient | None = None) -> None:
        self.aion = aion or AIONBrainClient()

    @staticmethod
    def default_user_key() -> str:
        return settings.gmail_impersonate_subject or "me"

    async def collect_samples(
        self, session: AsyncSession, user_key: str, limit: int = 100
    ) -> list[str]:
        """Most-recent authored bodies from SENT emails (quotes stripped)."""
        stmt = (
            select(Email)
            .where(Email.status == EmailStatus.SENT)
            .order_by(Email.received_at.desc().nullslast(), Email.created_at.desc())
            .limit(limit)
        )
        rows = (await session.scalars(stmt)).all()
        bodies = [e.body_text for e in rows]

        # Cold start: too few persisted SENT emails → seed from the Gmail SENT label.
        if len([b for b in bodies if (b or "").strip()]) < _MIN_DB_SAMPLES:
            try:
                bodies += await self._gmail_sent_bodies(_GMAIL_SEED_MAX)
            except Exception as exc:  # noqa: BLE001
                logger.warning("style seed from Gmail SENT failed: %s", exc)

        samples: list[str] = []
        total = 0
        for body in bodies:
            txt = _authored_text(body)
            if len(txt) < 20:  # skip near-empty
                continue
            if total + len(txt) > _MAX_TOTAL_CHARS:
                break
            samples.append(txt)
            total += len(txt)
        return samples

    async def _gmail_sent_bodies(self, max_total: int) -> list[str]:
        """Pull recent bodies from the Gmail 'SENT' label (blocking API off-thread)."""
        from backend.services.email.gmail_connector import GmailConnector

        conn = GmailConnector()

        def _pull() -> list[str]:
            ids = conn.list_message_ids(label_ids=["SENT"], max_total=max_total)
            out: list[str] = []
            for mid in ids:
                try:
                    out.append(conn.fetch_normalized(mid).body_text or "")
                except Exception:  # noqa: BLE001
                    continue
            return out

        return await asyncio.to_thread(_pull)

    async def learn(
        self, session: AsyncSession, user_key: str | None = None, limit: int = 100
    ) -> StyleProfile:
        """Analyze SENT emails, extract a style profile, and upsert it."""
        user_key = user_key or self.default_user_key()
        samples = await self.collect_samples(session, user_key, limit=limit)

        if not samples:
            profile = dict(_DEFAULT_PROFILE)
            profile["source"] = "default_no_samples"
            return await self._upsert(session, user_key, profile, sample_size=0)

        joined = "\n\n---\n\n".join(f"[{i + 1}] {s}" for i, s in enumerate(samples))
        prompt = _STYLE_PROMPT.format(samples=joined)
        profile = dict(_DEFAULT_PROFILE)
        profile["source"] = "fallback"
        try:
            resp = await self.aion.orchestrate(prompt, task_type="medium", priority="P2")
            data = _parse_json_block(resp.get("text", "")) if resp.get("ok", True) else None
            if data:
                profile = self._normalize(data)
                profile["source"] = "llm"
        except Exception as exc:  # noqa: BLE001
            logger.warning("style learn AION failed: %s", exc)

        return await self._upsert(session, user_key, profile, sample_size=len(samples))

    async def get_profile(
        self, session: AsyncSession, user_key: str | None = None
    ) -> StyleProfile | None:
        user_key = user_key or self.default_user_key()
        return await session.scalar(
            select(StyleProfile).where(StyleProfile.user_key == user_key)
        )

    # ── helpers ─────────────────────────────────────────────
    @staticmethod
    def _normalize(data: dict) -> dict:
        out = dict(_DEFAULT_PROFILE)
        for k in (
            "language_primary", "formality", "greeting", "signoff",
            "avg_email_length", "emoji_usage",
        ):
            if data.get(k):
                out[k] = str(data[k]).strip()
        if isinstance(data.get("tone_descriptors"), list):
            out["tone_descriptors"] = [str(x).strip() for x in data["tone_descriptors"]][:5]
        if isinstance(data.get("common_phrases"), list):
            out["common_phrases"] = [str(x).strip() for x in data["common_phrases"]][:8]
        out["bullet_preference"] = bool(data.get("bullet_preference", False))
        return out

    async def _upsert(
        self, session: AsyncSession, user_key: str, profile: dict, sample_size: int
    ) -> StyleProfile:
        row = await session.scalar(
            select(StyleProfile).where(StyleProfile.user_key == user_key)
        )
        if row is None:
            row = StyleProfile(user_key=user_key, profile=profile, sample_size=sample_size)
            session.add(row)
        else:
            row.profile = profile
            row.sample_size = sample_size
        await session.flush()
        return row

    @staticmethod
    def directive(profile: dict | None) -> str:
        """Compact NL instruction to steer the reply prompt toward Manny's style."""
        if not profile:
            return ""
        p = profile
        parts = [
            f"Escribe imitando el estilo de Manuel Cadena. Idioma: {p.get('language_primary', 'es')}.",
            f"Registro: {p.get('formality', 'neutral')}.",
        ]
        tones = p.get("tone_descriptors") or []
        if tones:
            parts.append(f"Tono: {', '.join(tones)}.")
        if p.get("greeting"):
            parts.append(f"Saludo típico: \"{p['greeting']}\".")
        if p.get("signoff"):
            parts.append(f"Despedida típica: \"{p['signoff']}\".")
        parts.append(f"Longitud: {p.get('avg_email_length', 'medium')}.")
        emoji = p.get("emoji_usage", "none")
        parts.append("Sin emojis." if emoji == "none" else f"Emojis: {emoji}.")
        phrases = p.get("common_phrases") or []
        if phrases:
            parts.append(f"Puede usar frases suyas como: {'; '.join(phrases[:4])}.")
        if p.get("bullet_preference"):
            parts.append("Prefiere listas con viñetas cuando aplica.")
        return " ".join(parts)
