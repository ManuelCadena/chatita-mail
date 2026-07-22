"""
Chatita Mail v3.0 — Stage 2: LLM zero-shot classifier.

Research basis:
  - Chikodi (2025): deployed assistant reached 92.4% accuracy on multi-category.
  - Zhang et al. (2021): pass thread/relationship context for intent understanding.

Only invoked for emails the lexical pre-filter could not confidently classify.
Uses AION Brain task_type="simple" (Together Llama-3.3) to minimize cost.
"""
from __future__ import annotations

import json
import logging

from backend.ai.aion_client import AIONBrainClient
from backend.models.entities import EmailCategory

logger = logging.getLogger("chatita_mail.classifier")

_VALID = {c.value for c in EmailCategory}

_PROMPT_TEMPLATE = """You are an expert email triage classifier. Classify the email into EXACTLY one category.

Categories:
- CRITICAL: requires immediate action (boss, client emergency, hard deadline today)
- IMPORTANT: requires action within 24h (work request, personal important)
- MEDIUM: can wait 1-2 days (FYI needing eventual reply)
- LOW: no action needed, informational
- SPAM: marketing/promotions/newsletters the user never reads
- NOISE: automated notifications, receipts, confirmations

Sender relationship context: {relationship}

Email:
From: {from_name} <{from_address}>
Subject: {subject}
Body (truncated):
{body}

Return ONLY valid JSON, no prose:
{{
  "category": "CRITICAL|IMPORTANT|MEDIUM|LOW|SPAM|NOISE",
  "confidence": 0.0-1.0,
  "reasoning": "1-2 sentences explaining WHY (this is shown to the user as XAI)"
}}"""


class LLMClassifier:
    """Stage-2 classifier backed by AION Brain."""

    def __init__(self, aion: AIONBrainClient | None = None) -> None:
        from backend.ai.aion_client import aion as default_aion

        self.aion = aion or default_aion

    async def classify(
        self,
        from_address: str,
        from_name: str | None,
        subject: str | None,
        body_text: str | None,
        relationship: str = "unknown",
    ) -> dict:
        prompt = _PROMPT_TEMPLATE.format(
            relationship=relationship,
            from_name=from_name or "",
            from_address=from_address,
            subject=subject or "(no subject)",
            body=(body_text or "")[:1500],
        )

        result = await self.aion.orchestrate(prompt=prompt, task_type="simple")
        text = result.get("text", "") if isinstance(result, dict) else str(result)

        parsed = self._parse(text)
        if parsed is None:
            # Fallback: safe default that keeps important mail visible.
            logger.warning("LLM classifier could not parse output; defaulting to MEDIUM")
            return {
                "category": EmailCategory.MEDIUM,
                "confidence": 0.5,
                "reasoning": "Could not parse classifier output; defaulted to MEDIUM to avoid hiding a possibly important email.",
            }
        return parsed

    @staticmethod
    def _parse(text: str) -> dict | None:
        # Extract first JSON object from the model output.
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None

        cat = str(data.get("category", "")).upper().strip()
        if cat not in _VALID:
            return None
        try:
            conf = float(data.get("confidence", 0.5))
        except (TypeError, ValueError):
            conf = 0.5
        conf = max(0.0, min(1.0, conf))
        return {
            "category": EmailCategory(cat),
            "confidence": conf,
            "reasoning": str(data.get("reasoning", "")).strip() or None,
        }
