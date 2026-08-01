"""
Chatita Mail v3.0 — Google Drive connector (T4.2 attachment auto-suggest).

Read-only Drive access via the same service account + Domain-Wide Delegation
used for Gmail (impersonates jose@manuelcadena.com). Scope: drive.readonly.

Used to suggest files when the user mentions an attachment in a reply, so they
can insert a shareable link without leaving the composer.
"""
from __future__ import annotations

import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build

from backend.config import settings

logger = logging.getLogger("chatita_mail.drive")

_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Human-friendly labels for the most common Drive MIME types.
_MIME_LABELS = {
    "application/vnd.google-apps.document": "Doc",
    "application/vnd.google-apps.spreadsheet": "Sheet",
    "application/vnd.google-apps.presentation": "Slides",
    "application/vnd.google-apps.folder": "Carpeta",
    "application/pdf": "PDF",
}


class DriveConnector:
    def __init__(self) -> None:
        self.key_path = settings.google_service_account_json
        self.subject = settings.gmail_impersonate_subject
        self._svc = None

    @staticmethod
    def enabled() -> bool:
        # Drive shares the Gmail service account; it's available whenever that
        # credential path is configured (scope authorized via DWD).
        return bool(settings.google_service_account_json)

    def _service(self):
        if self._svc is None:
            creds = service_account.Credentials.from_service_account_file(
                self.key_path, scopes=_SCOPES, subject=self.subject
            )
            self._svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        return self._svc

    @staticmethod
    def _label(mime: str) -> str:
        return _MIME_LABELS.get(mime, (mime.split("/")[-1] or "archivo")[:12])

    def search(self, query: str, limit: int = 8) -> list[dict]:
        """Search non-trashed Drive files by full text; newest first."""
        limit = max(1, min(limit, 25))
        q_parts = ["trashed = false"]
        clean = (query or "").replace("'", "").replace("\\", "").strip()
        if clean:
            q_parts.append(f"fullText contains '{clean}'")
        q = " and ".join(q_parts)
        resp = (
            self._service()
            .files()
            .list(
                q=q,
                pageSize=limit,
                orderBy="modifiedTime desc",
                fields="files(id,name,mimeType,modifiedTime,webViewLink,iconLink,size)",
                spaces="drive",
                corpora="user",
            )
            .execute()
        )
        out = []
        for f in resp.get("files", []):
            out.append(
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "mimeType": f.get("mimeType"),
                    "kind": self._label(f.get("mimeType", "")),
                    "link": f.get("webViewLink"),
                    "icon": f.get("iconLink"),
                    "modified": f.get("modifiedTime"),
                    "size": int(f["size"]) if f.get("size") else None,
                }
            )
        return out
