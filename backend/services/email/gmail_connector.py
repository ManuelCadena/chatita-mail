"""
Chatita Mail v3.0 - Gmail connector.

Reuses Chatita's existing Google Service Account with Domain-Wide Delegation
(same mechanism as chatita-local/tools/google-service-auth.js). No per-user OAuth
flow is required: the service account impersonates the target mailbox.

Scopes: gmail.readonly (read/sync) + gmail.send (reply/forward/compose). The
same service account already has gmail.send authorized via Domain-Wide
Delegation (chatita-local/tools/hub-gmail.js uses it in production).
"""
from __future__ import annotations

import base64
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.utils import parsedate_to_datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.config import settings

logger = logging.getLogger("chatita_mail.gmail")

_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


class HistoryExpiredError(Exception):
    """Raised when startHistoryId is too old (Gmail 404) → caller must full-resync."""


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

    # ── Full-sync / incremental primitives ──────────────────────

    def get_profile_history_id(self) -> str | None:
        """Current mailbox historyId — used as the anchor for future deltas."""
        try:
            profile = self._get_service().users().getProfile(userId="me").execute()
            hid = profile.get("historyId")
            return str(hid) if hid is not None else None
        except Exception as exc:  # noqa: BLE001
            logger.warning("get_profile_history_id failed: %s", exc)
            return None

    def list_message_ids(
        self,
        query: str | None = None,
        label_ids: list[str] | None = None,
        unread_only: bool = False,
        max_total: int | None = None,
        page_size: int = 500,
    ) -> list[str]:
        """
        Paginate messages.list and collect message IDs (newest first).

        Args:
            query: Gmail search query (e.g. "in:inbox", "after:2024/01/01").
            label_ids: restrict to labels (default INBOX). Pass [] for ALL mail.
            max_total: stop after this many IDs (None = every message).
            page_size: per-page cap (Gmail max 500).
        """
        svc = self._get_service()
        if label_ids is None:
            label_ids = ["INBOX"]
        if unread_only:
            label_ids = list(label_ids) + ["UNREAD"]

        ids: list[str] = []
        page_token: str | None = None
        while True:
            remaining = None if max_total is None else max_total - len(ids)
            if remaining is not None and remaining <= 0:
                break
            this_page = page_size if remaining is None else min(page_size, remaining)
            req = svc.users().messages().list(
                userId="me",
                labelIds=label_ids or None,
                q=query,
                maxResults=min(this_page, 500),
                pageToken=page_token,
            )
            resp = req.execute()
            ids.extend(m["id"] for m in resp.get("messages", []) if m.get("id"))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return ids if max_total is None else ids[:max_total]

    def list_history_added(
        self, start_history_id: str, label_id: str = "INBOX"
    ) -> tuple[list[str], str | None]:
        """
        Return (added_message_ids, new_history_id) since start_history_id via
        users.history.list (messageAdded). Raises HistoryExpiredError on 404.
        """
        svc = self._get_service()
        added: list[str] = []
        page_token: str | None = None
        new_history_id: str | None = None
        try:
            while True:
                resp = (
                    svc.users()
                    .history()
                    .list(
                        userId="me",
                        startHistoryId=start_history_id,
                        historyTypes=["messageAdded"],
                        labelId=label_id or None,
                        pageToken=page_token,
                    )
                    .execute()
                )
                if resp.get("historyId"):
                    new_history_id = str(resp["historyId"])
                for h in resp.get("history", []):
                    for ma in h.get("messagesAdded", []) or []:
                        msg = ma.get("message", {})
                        mid = msg.get("id")
                        if mid:
                            added.append(mid)
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break
        except HttpError as exc:
            if getattr(exc, "resp", None) is not None and exc.resp.status == 404:
                raise HistoryExpiredError(str(exc)) from exc
            raise
        # de-dup preserving order
        seen: set[str] = set()
        deduped = [m for m in added if not (m in seen or seen.add(m))]
        return deduped, new_history_id

    def fetch_normalized(self, message_id: str) -> NormalizedEmail:
        """Public: fetch + parse a single message by id."""
        return self._fetch_and_normalize(self._get_service(), message_id)

    # ── Send / compose primitives (gmail.send) ──────────────────

    def get_headers(self, message_id: str) -> dict:
        """Fetch RFC822 threading headers of a message (for proper reply chains)."""
        svc = self._get_service()
        msg = (
            svc.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Message-ID", "References", "Subject", "From", "To", "Cc"],
            )
            .execute()
        )
        headers = (msg.get("payload") or {}).get("headers", [])
        return {
            "message_id": _header(headers, "Message-ID"),
            "references": _header(headers, "References"),
            "subject": _header(headers, "Subject"),
            "from": _header(headers, "From"),
            "to": _header(headers, "To"),
            "cc": _header(headers, "Cc"),
            "thread_id": msg.get("threadId"),
        }

    def get_attachment_bytes(self, message_id: str, attachment_id: str) -> bytes:
        """Download raw bytes of one attachment (used when forwarding)."""
        svc = self._get_service()
        att = (
            svc.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=message_id, id=attachment_id)
            .execute()
        )
        data = att.get("data", "")
        padded = data + "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(padded)

    def send_message(
        self,
        *,
        to: list[str],
        subject: str,
        body_text: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        thread_id: str | None = None,
        in_reply_to: str | None = None,
        references: str | None = None,
        attachments: list[dict] | None = None,
    ) -> dict:
        """
        Send an email as the impersonated mailbox. Returns {id, threadId}.

        attachments: list of {filename, mime_type, data(bytes)}.
        Threading: pass thread_id (Gmail) + in_reply_to/references (RFC Message-ID)
        so replies chain correctly in every client.
        """
        to = [a for a in (to or []) if a]
        if not to:
            raise ValueError("send_message requires at least one recipient")

        if attachments:
            msg: MIMEText | MIMEMultipart = MIMEMultipart("mixed")
            msg.attach(MIMEText(body_text or "", "plain", "utf-8"))
            for att in attachments:
                part = MIMEBase(*(att.get("mime_type") or "application/octet-stream").split("/", 1))
                part.set_payload(att.get("data") or b"")
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=att.get("filename") or "attachment",
                )
                msg.attach(part)
        else:
            msg = MIMEText(body_text or "", "plain", "utf-8")

        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join([a for a in cc if a])
        if bcc:
            msg["Bcc"] = ", ".join([a for a in bcc if a])
        msg["From"] = self.subject
        msg["Subject"] = subject or ""
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = (f"{references} {in_reply_to}".strip() if references else in_reply_to)

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        body: dict = {"raw": raw}
        if thread_id:
            body["threadId"] = thread_id
        sent = self._get_service().users().messages().send(userId="me", body=body).execute()
        logger.info(
            "Gmail send ok: to=%s subject=%r thread=%s msg=%s",
            to, (subject or "")[:80], sent.get("threadId"), sent.get("id"),
        )
        return {"id": sent.get("id"), "threadId": sent.get("threadId")}

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
