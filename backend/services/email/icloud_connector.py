"""
Chatita Mail v3.0 - iCloud connector.

Connects via IMAP over SSL (imap.mail.me.com:993) using an app-specific password.
To generate one: appleid.apple.com → Security → App-Specific Passwords.

Shares NormalizedEmail with gmail_connector so sync.py + triage accept both providers.
Supports incremental sync via IMAP UID + SINCE date filter.
"""
from __future__ import annotations

import email as email_lib
import imaplib
import logging
import re
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime

from backend.config import settings
from backend.services.email.gmail_connector import NormalizedEmail

logger = logging.getLogger("chatita_mail.icloud")

_IMAP_HOST = "imap.mail.me.com"
_IMAP_PORT = 993
_DATE_FMT = "%d-%b-%Y"  # IMAP SEARCH SINCE format: "01-Jan-2026"


def _decode_header_value(raw: str | bytes | None) -> str:
    """Decode RFC-2047 encoded header (handles UTF-8, Base64, QP)."""
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw if isinstance(raw, str) else raw.decode("utf-8", errors="replace"))))
    except Exception:  # noqa: BLE001
        return str(raw) if raw else ""


def _parse_addr(raw: str) -> tuple[str, str | None]:
    """Split 'Name <email@x>' into (email, name)."""
    raw = (raw or "").strip()
    if "<" in raw and ">" in raw:
        name = raw[: raw.index("<")].strip().strip('"') or None
        addr = raw[raw.index("<") + 1 : raw.index(">")].strip()
        return addr, name
    return raw, None


def _split_addresses(raw: str) -> list[str]:
    if not raw:
        return []
    return [a.strip() for a in raw.split(",") if a.strip()]


def _extract_body_imap(msg: email_lib.message.Message) -> tuple[str, str]:
    """Recursively extract (plain, html) from a parsed email.message.Message."""
    plain, html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition") or "")
            if "attachment" in cd:
                continue
            charset = part.get_content_charset() or "utf-8"
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            decoded = payload.decode(charset, errors="replace")
            if ct == "text/plain":
                plain += decoded
            elif ct == "text/html":
                html += decoded
    else:
        ct = msg.get_content_type()
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            decoded = payload.decode(charset, errors="replace")
            if ct == "text/html":
                html = decoded
            else:
                plain = decoded
    return plain, html


def _collect_attachments_imap(msg: email_lib.message.Message) -> list[dict]:
    atts = []
    for part in msg.walk():
        cd = str(part.get("Content-Disposition") or "")
        if "attachment" not in cd:
            continue
        filename = _decode_header_value(part.get_filename() or "")
        atts.append(
            {
                "filename": filename or "attachment",
                "mimeType": part.get_content_type(),
                "size": len(part.get_payload(decode=True) or b""),
            }
        )
    return atts


def _html_to_text_simple(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()


class ICloudConnector:
    """Reads a mailbox via iCloud IMAP (app-specific password required)."""

    def __init__(
        self,
        username: str | None = None,
        app_password: str | None = None,
    ) -> None:
        self.username = username or settings.icloud_username
        self.app_password = app_password or settings.icloud_app_password

    def _connect(self) -> imaplib.IMAP4_SSL:
        """Open a fresh authenticated IMAP4_SSL connection."""
        imap = imaplib.IMAP4_SSL(_IMAP_HOST, _IMAP_PORT)
        imap.login(self.username, self.app_password)
        return imap

    def health(self) -> dict:
        """Verify IMAP connectivity. Never raises."""
        try:
            imap = self._connect()
            status, data = imap.select("INBOX", readonly=True)
            exists = int(data[0]) if status == "OK" and data and data[0] else 0
            imap.logout()
            return {"ok": True, "email": self.username, "inbox_count": exists}
        except Exception as exc:  # noqa: BLE001
            logger.warning("iCloud health failed: %s", exc)
            return {"ok": False, "error": str(exc), "email": self.username}

    def list_inbox(
        self,
        max_results: int = 10,
        unread_only: bool = False,
        since_date: datetime | None = None,
    ) -> list[NormalizedEmail]:
        """
        Fetch recent INBOX messages.

        Args:
            max_results: cap on messages returned (newest first).
            unread_only: if True, only UNSEEN messages.
            since_date: if set, only messages received on/after this date
                        (incremental sync anchor).
        """
        imap = self._connect()
        try:
            imap.select("INBOX", readonly=True)

            # Build IMAP SEARCH criteria
            criteria_parts: list[str] = []
            if unread_only:
                criteria_parts.append("UNSEEN")
            if since_date:
                criteria_parts.append(f'SINCE "{since_date.strftime(_DATE_FMT)}"')
            criteria = " ".join(criteria_parts) if criteria_parts else "ALL"

            status, data = imap.search(None, criteria)
            if status != "OK" or not data or not data[0]:
                return []

            # UIDs are space-separated bytes; take the last max_results
            uids = data[0].split()
            uids = uids[-max_results:]  # newest UIDs are at the end
            uids.reverse()              # newest first

            out: list[NormalizedEmail] = []
            for uid in uids:
                try:
                    ne = self._fetch_and_normalize(imap, uid)
                    if ne:
                        out.append(ne)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse iCloud message %s: %s", uid, exc)
            return out
        finally:
            try:
                imap.logout()
            except Exception:  # noqa: BLE001
                pass

    def _fetch_and_normalize(
        self, imap: imaplib.IMAP4_SSL, uid: bytes
    ) -> NormalizedEmail | None:
        status, data = imap.fetch(uid, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            return None

        raw_bytes = data[0][1] if isinstance(data[0], tuple) else data[0]
        if not isinstance(raw_bytes, bytes):
            return None

        msg = email_lib.message_from_bytes(raw_bytes)

        from_raw = _decode_header_value(msg.get("From") or "")
        from_email, from_name = _parse_addr(from_raw)

        to_raw = _decode_header_value(msg.get("To") or "")
        cc_raw = _decode_header_value(msg.get("Cc") or "")
        subject = _decode_header_value(msg.get("Subject") or "")

        plain, html = _extract_body_imap(msg)
        body_text = plain.strip() or _html_to_text_simple(html)

        received_at: str | None = None
        date_hdr = msg.get("Date")
        if date_hdr:
            try:
                dt = parsedate_to_datetime(date_hdr)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                received_at = dt.isoformat()
            except Exception:  # noqa: BLE001
                received_at = None

        # Use Message-ID as provider_message_id; fall back to IMAP sequence UID
        message_id = (msg.get("Message-ID") or "").strip().strip("<>")
        if not message_id:
            message_id = f"icloud-uid-{uid.decode()}"

        snippet = body_text[:200] if body_text else (subject or "")[:200]

        return NormalizedEmail(
            provider_message_id=message_id,
            thread_id=msg.get("Thread-Topic") or msg.get("References") or None,
            from_address=from_email,
            from_name=from_name,
            to_addresses=_split_addresses(to_raw),
            cc_addresses=_split_addresses(cc_raw),
            subject=subject or None,
            body_text=body_text[:50_000] if body_text else None,
            body_html=html.strip()[:200_000] if html and html.strip() else None,
            snippet=snippet,
            received_at=received_at,
            attachments=_collect_attachments_imap(msg),
        )
