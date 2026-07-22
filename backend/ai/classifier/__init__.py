"""
Chatita Mail v3.0 — 2-Stage Email Classifier.

Stage 1 (lexical): fast, $0, handles obvious cases (~2ms, Jáñez-Martino 2023).
Stage 2 (LLM):      AION Brain zero-shot for ambiguous cases (Chikodi 2025).

Cost optimization: only ~20-30% of emails reach the LLM.
"""
from __future__ import annotations

import logging

from backend.ai.classifier.lexical_prefilter import LexicalPreFilter, LexicalResult
from backend.ai.classifier.llm_classifier import LLMClassifier
from backend.config import settings
from backend.models.entities import EmailCategory
from backend.models.schemas import ClassificationResult

logger = logging.getLogger("chatita_mail.classifier")


class EmailClassifier:
    """Orchestrates the 2-stage classification pipeline."""

    def __init__(
        self,
        lexical: LexicalPreFilter | None = None,
        llm: LLMClassifier | None = None,
        threshold: float | None = None,
    ) -> None:
        self.lexical = lexical or LexicalPreFilter()
        self.llm = llm or LLMClassifier()
        self.threshold = threshold or settings.lexical_confidence_threshold

    async def classify(
        self,
        from_address: str,
        from_name: str | None = None,
        subject: str | None = None,
        body_text: str | None = None,
        raw_headers: str | None = None,
        relationship: str = "unknown",
    ) -> ClassificationResult:
        # ── Stage 1: lexical ────────────────────────────────
        lex: LexicalResult = self.lexical.classify(
            from_address=from_address,
            subject=subject,
            body_text=body_text,
            raw_headers=raw_headers,
        )

        if (
            lex.category != EmailCategory.UNCLASSIFIED
            and lex.confidence >= self.threshold
        ):
            return ClassificationResult(
                category=lex.category,
                confidence=lex.confidence,
                stage="lexical",
                reasoning=f"Matched lexical signals: {', '.join(lex.matched_signals) or 'n/a'}",
                is_newsletter=lex.is_newsletter,
                unsubscribe_url=lex.unsubscribe_url,
            )

        # ── Stage 2: LLM (ambiguous / low-confidence) ───────
        llm_out = await self.llm.classify(
            from_address=from_address,
            from_name=from_name,
            subject=subject,
            body_text=body_text,
            relationship=relationship,
        )
        return ClassificationResult(
            category=llm_out["category"],
            confidence=llm_out["confidence"],
            stage="llm",
            reasoning=llm_out.get("reasoning"),
            is_newsletter=lex.is_newsletter,
            unsubscribe_url=lex.unsubscribe_url,
        )


__all__ = ["EmailClassifier", "LexicalPreFilter", "LLMClassifier"]
