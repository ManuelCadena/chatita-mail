"""
Chatita Mail v3.0 — Pydantic schemas (API request/response models).
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.models.entities import EmailCategory, EmailStatus, RiskLevel


# ── Email ───────────────────────────────────────────────────
class EmailIn(BaseModel):
    """Normalized email used across the pipeline (provider-agnostic)."""

    provider_message_id: str
    thread_id: str | None = None
    from_address: str
    from_name: str | None = None
    to_addresses: list[str] = Field(default_factory=list)
    cc_addresses: list[str] = Field(default_factory=list)
    subject: str | None = None
    body_text: str | None = None
    body_html: str | None = None
    snippet: str | None = None
    attachments: list[dict] = Field(default_factory=list)
    received_at: datetime | None = None


class EmailOut(BaseModel):
    id: str
    from_address: str
    from_name: str | None
    subject: str | None
    snippet: str | None
    status: EmailStatus
    is_read: bool
    received_at: datetime | None
    category: EmailCategory | None = None
    confidence: float | None = None
    risk_level: RiskLevel | None = None
    risk_score: int | None = None

    model_config = {"from_attributes": True}


# ── Classification ──────────────────────────────────────────
class ClassificationResult(BaseModel):
    category: EmailCategory
    confidence: float
    stage: str  # lexical | llm
    reasoning: str | None = None
    is_newsletter: bool = False
    unsubscribe_url: str | None = None


class ReclassifyIn(BaseModel):
    category: EmailCategory


# ── Security ────────────────────────────────────────────────
class SecurityResult(BaseModel):
    risk_score: int
    risk_level: RiskLevel
    event_type: str
    risk_factors: list[str] = Field(default_factory=list)
    explanation: str | None = None
    recommended_action: str  # allow | quarantine | block
    sender_reputation: dict | None = None


# ── Health ──────────────────────────────────────────────────
class HealthOut(BaseModel):
    status: str
    version: str
    environment: str
    database: bool
    redis: bool
    aion_brain: dict
