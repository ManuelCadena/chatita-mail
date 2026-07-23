"""
Chatita Mail v3.0 — Configuration
Centralized settings loaded from environment variables.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Server ──────────────────────────────────────────────
    app_name: str = "Chatita Mail"
    app_version: str = "3.0.0-alpha"
    environment: Literal["development", "production"] = "development"
    port: int = 8000
    secret_key: str = "change-me-in-production"

    # ── Database ────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://manuelcadena@localhost:5432/chatita_mail"
    database_url_sync: str = "postgresql://manuelcadena@localhost:5432/chatita_mail"
    redis_url: str = "redis://localhost:6379/0"

    # ── AION Brain ──────────────────────────────────────────
    # Mode: "http" (recommended for prod) or "stdio" (local MCP)
    aion_mode: Literal["http", "stdio"] = "http"
    aion_brain_url: str = "http://localhost:3100"
    aion_brain_mcp_path: str = "/opt/aion-brain/mcp-server.js"
    aion_timeout_seconds: int = 60
    # API key sent as X-API-Key to AION Brain (required in prod; local dev may
    # leave empty if AION_AUTH_DISABLED=1 on the server).
    aion_api_key: str = ""
    # If AION Brain is unreachable, fall back to a local heuristic
    aion_allow_fallback: bool = True

    # ── Email Accounts ──────────────────────────────────────
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_refresh_token: str = ""
    icloud_username: str = ""
    icloud_app_password: str = ""

    # ── Google Workspace ────────────────────────────────────
    # Path to the service-account JSON key (Domain-Wide Delegation).
    # Reuses Chatita's existing service account by default.
    google_service_account_json: str = "/Users/manuelcadena/chatita-local/chatita-service-account.json"
    # Mailbox to impersonate via DWD (Manny's primary inbox).
    gmail_impersonate_subject: str = "jose@manuelcadena.com"

    # ── Communication ───────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # ── Classification thresholds (research-driven) ─────────
    # Jáñez-Martino: lexical prefilter is fast/cheap; escalate to LLM only if ambiguous
    lexical_confidence_threshold: float = 0.90
    # Chikodi 2025: production target accuracy
    min_classification_accuracy: float = 0.92
    # Phishing risk thresholds
    phishing_quarantine_threshold: int = 70
    phishing_block_threshold: int = 90

    # ── Logging ─────────────────────────────────────────────
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()


settings = get_settings()
