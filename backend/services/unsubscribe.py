"""
Chatita Mail v3.0 - Intelligent auto-unsubscribe.

Research basis:
  - Dredze et al. (2008) & Mathew (2026): removing never-read newsletters is the
    single biggest lever for reducing inbox noise.

Strategy:
  1. Only act on emails classified SPAM/LOW that are newsletters.
  2. Prefer RFC 8058 One-Click (List-Unsubscribe-Post) when available.
  3. Otherwise GET the unsubscribe URL. Never submit credentials/forms blindly.
"""
from __future__ import annotations

import logging

import httpx

logger = logging.getLogger("chatita_mail.unsubscribe")


class Unsubscriber:
    async def unsubscribe(
        self,
        unsubscribe_url: str | None,
        list_unsubscribe_post: str | None = None,
    ) -> dict:
        """
        Attempt to unsubscribe. Returns {ok, method, detail}.
        Safe by design: only follows unsubscribe links, never posts secrets.
        """
        if not unsubscribe_url and not list_unsubscribe_post:
            return {"ok": False, "method": "none", "detail": "No unsubscribe link found"}

        # RFC 8058 One-Click
        if list_unsubscribe_post and unsubscribe_url and unsubscribe_url.startswith("http"):
            try:
                async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                    resp = await client.post(
                        unsubscribe_url,
                        data={"List-Unsubscribe": "One-Click"},
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                    return {
                        "ok": resp.status_code < 400,
                        "method": "one-click",
                        "detail": f"HTTP {resp.status_code}",
                    }
            except Exception as exc:  # noqa: BLE001
                logger.warning("One-click unsubscribe failed: %s", exc)

        # Plain GET
        if unsubscribe_url and unsubscribe_url.startswith("http"):
            try:
                async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                    resp = await client.get(unsubscribe_url)
                    return {
                        "ok": resp.status_code < 400,
                        "method": "get",
                        "detail": f"HTTP {resp.status_code}",
                    }
            except Exception as exc:  # noqa: BLE001
                logger.warning("GET unsubscribe failed: %s", exc)
                return {"ok": False, "method": "get", "detail": str(exc)}

        return {"ok": False, "method": "unsupported", "detail": "Only http(s) links supported"}
