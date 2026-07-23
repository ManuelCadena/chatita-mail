"""
Chatita Mail v3.0 - Gmail connector.

Reuses Chatita's existing Google Service Account with Domain-Wide Delegation
(same mechanism as chatita-local/tools/google-service-auth.js). No per-user OAuth
flow is required: the service account impersonates the target mailbox.

Scope: gmail.readonly (Phase 1 only reads; sending/modify added later).
"""
from __future__ import annotations

import base64
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build

from backend.config import settings

logger = logging.getLogger("chatita_mail.gmail")

_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@dataclass
class NormalizedEmail:
    """Provider-agnostic email ready to POST to /api/inbox/ingest."""

    provider_message_id: str
    thread_id: str | None
    from_address: str
    from_name: str | None
    to_addresses: list[str]
    cc_addresses: list[str]
    subject: str | None
    body_text: str | None
    snippet: str | None
    received_at: str | None
    body_html: str | None = None
    attachments: list[dict] = field(default_factory=list)

    def to_payload(self) -> dict:
        return {
            "provider_message_id": self.provider_message_id,
            "thread_id": self.thread_id,
            "from_address": self.from_address,
            "from_name": self.from_name,
            "to_addresses": self.to_addresses,
            "cc_addresses": self.cc_addresses,
            "subject": self.subject,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "snippet": self.snippet,
            "received_at": self.received_at,
            "attachments": self.attachments,
        }


def _b64url_decode(data: str) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return ""


def _parse_addr(raw: str) -> tuple[str, str | None]:
    """Split 'Name <email@x>' into (email, name)."""
    raw = (raw or "").strip()
    if "<" in raw and ">" in raw:
        name = raw[: raw.index("<")].strip().strip('"') or None
        email = raw[raw.index("<") + 1 : raw.index(">")].strip()
        return email, name
    return raw, None


def _header(headers: list[dict], name: str) -> str:
    for h in headers or []:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _extract_body(payload: dict, depth: int = 0) -> tuple[str, str]:
    """Recursively collect (plain, html) body text from a Gmail payload."""
    plain, html = "", ""
    if depth > 12 or not payload:
        return plain, html
    mime = (payload.get("mimeType") or "").lower()
    body_data = (payload.get("body") or {}).get("data")
    filename = payload.get("filename")

    if mime == "text/plain" and body_data:
        plain += _b64url_decode(body_data)
    elif mime == "text/html" and body_data:
        html += _b64url_decode(body_data)
    elif payload.get("parts"):
        for part in payload["parts"]:
            if part.get("filename"):
                continue
            p, h = _extract_body(part, depth + 1)
            plain += p
            html += h
    elif body_data and not filename and not mime.startswith(("image/", "application/")):
        plain += _b64url_decode(body_data)
    return plain, html


def _collect_attachments(payload: dict, acc: list[dict] | None = None) -> list[dict]:
    acc = acc if acc is not None else []
    if not payload:
        return acc
    body = payload.get("body") or {}
    if payload.get("filename") and body.get("attachmentId"):
        acc.append(
            {
                "filename": payload["filename"],
                "mimeType": payload.get("mimeType"),
                "size": body.get("size"),
                "attachmentId": body["attachmentId"],
            }
        )
    for part in payload.get("parts", []) or []:
        _collect_attachments(part, acc)
    return acc


class GmailConnector:
    """Reads Manny's Gmail inbox via service-account delegation."""

    def __init__(
        self,
        key_path: str | None = None,
        subject: str | None = None,
    ) -> None:
        self.key_path = key_path or settings.google_service_account_json
        self.subject = subject or settings.gmail_impersonate_subject
        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service
        creds = service_account.Credentials.from_service_account_file(
            self.key_path, scopes=_SCOPES, subject=self.subject
        )
        self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return self._service

    def health(self) -> dict:
        """Verify delegation works. Never raises."""
        try:
            svc = self._get_service()
            profile = svc.users().getProfile(userId="me").execute()
            return {
                "ok": True,
                "email": profile.get("emailAddress"),
                "messages_total": profile.get("messagesTotal"),
                "subject": self.subject,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gmail health failed: %s", exc)
            return {"ok": False, "error": str(exc), "subject": self.subject}

    def list_inbox(self, max_results: int = 10, unread_only: bool = False) -> list[NormalizedEmail]:
        """Fetch recent INBOX messages, fully parsed and normalized."""
        svc = self._get_service()
        label_ids = ["INBOX"]
        if unread_only:
            label_ids.append("UNREAD")
        listing = (
            svc.users()
            .messages()
            .list(userId="me", labelIds=label_ids, maxResults=min(max_results, 50))
            .execute()
        )
        out: list[NormalizedEmail] = []
        for meta in listing.get("messages", []):
            try:
                out.append(self._fetch_and_normalize(svc, meta["id"]))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to parse message %s: %s", meta.get("id"), exc)
        return out

    def _fetch_and_normalize(self, svc, message_id: str) -> NormalizedEmail:
        msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])

        from_email, from_name = _parse_addr(_header(headers, "From"))
        to_list = [a.strip() for a in _header(headers, "To").split(",") if a.strip()]
        cc_list = [a.strip() for a in _header(headers, "Cc").split(",") if a.strip()]

        plain, html = _extract_body(payload)
        body_text = plain.strip() or _html_to_text(html)

        received_at = None
        date_hdr = _header(headers, "Date")
        if date_hdr:
            try:
                dt = parsedate_to_datetime(date_hdr)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                received_at = dt.isoformat()
            except Exception:  # noqa: BLE001
                received_at = None

        return NormalizedEmail(
            provider_message_id=msg["id"],
            thread_id=msg.get("threadId"),
            from_address=from_email,
            from_name=from_name,
            to_addresses=to_list,
            cc_addresses=cc_list,
            subject=_header(headers, "Subject") or None,
            body_text=body_text[:50000] if body_text else None,
            body_html=html.strip()[:200000] if html and html.strip() else None,
            snippet=msg.get("snippet"),
            received_at=received_at,
            attachments=_collect_attachments(payload),
        )


def _html_to_text(html: str) -> str:
    """Minimal HTML→text fallback (full cleaning happens server-side if needed)."""
    if not html:
        return ""
    import re

    text = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()
