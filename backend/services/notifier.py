"""
Chatita Mail v3.0 - Telegram notifier.

Sends CRITICAL/IMPORTANT email alerts to Manny via AION Brain's telegram tool
(preferred) or directly via the Telegram Bot API as a fallback.
"""
from __future__ import annotations

import logging

import httpx

from backend.ai.aion_client import AIONBrainClient
from backend.config import settings

logger = logging.getLogger("chatita_mail.notifier")


class TelegramNotifier:
    def __init__(self, aion: AIONBrainClient | None = None) -> None:
        from backend.ai.aion_client import aion as default_aion

        self.aion = aion or default_aion

    async def notify(self, text: str) -> bool:
        """Return True if the message was sent by any transport."""
        # Preferred: AION Brain tool
        try:
            if settings.telegram_chat_id:
                res = await self.aion.execute_tool(
                    "telegram_send_message",
                    {"chat_id": settings.telegram_chat_id, "text": text},
                )
                if res and not res.get("fallback"):
                    return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("AION telegram tool failed: %s", exc)

        # Fallback: direct Bot API
        if settings.telegram_bot_token and settings.telegram_chat_id:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.post(
                        f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                        json={"chat_id": settings.telegram_chat_id, "text": text},
                    )
                    return resp.status_code == 200
            except Exception as exc:  # noqa: BLE001
                logger.warning("Direct telegram send failed: %s", exc)

        logger.info("Telegram not configured; skipping notification")
        return False

    @staticmethod
    def format_alert(category: str, from_address: str, subject: str | None, snippet: str | None) -> str:
        emoji = "🚨" if category == "CRITICAL" else "⭐"
        return (
            f"{emoji} {category} email\n\n"
            f"From: {from_address}\n"
            f"Subject: {subject or '(no subject)'}\n\n"
            f"{(snippet or '')[:300]}"
        )
