"""
Chatita Mail v3.0 — Google Calendar connector (Phase 2: T2.2 + T2.4).

Read/write Calendar access via the same service account + Domain-Wide
Delegation used for Gmail (impersonates jose@manuelcadena.com). Scopes
`calendar` + `calendar.events` are already authorized in the DWD client.

Used to:
  - T2.2: create a calendar event/reminder from a commitment (after user OK).
  - T2.4: compute free slots to propose meeting times, then create the event.

Human-in-the-loop: this connector only performs writes when a route explicitly
calls create_event (i.e. after the user confirmed in the UI). Detection and
slot proposal are read-only.
"""
from __future__ import annotations

import logging
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build

from backend.config import settings

logger = logging.getLogger("chatita_mail.calendar")

_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

# Manny's working timezone (Mexico). Slots are proposed within work hours here.
_TZ = ZoneInfo("America/Mexico_City")
_WORK_START = time(9, 0)
_WORK_END = time(18, 0)


class CalendarConnector:
    def __init__(self) -> None:
        self.key_path = settings.google_service_account_json
        self.subject = settings.gmail_impersonate_subject
        self._svc = None

    @staticmethod
    def enabled() -> bool:
        return bool(settings.google_service_account_json)

    def _service(self):
        if self._svc is None:
            creds = service_account.Credentials.from_service_account_file(
                self.key_path, scopes=_SCOPES, subject=self.subject
            )
            self._svc = build("calendar", "v3", credentials=creds, cache_discovery=False)
        return self._svc

    # ── Read: free/busy ─────────────────────────────────────
    def _busy_intervals(self, start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
        resp = (
            self._service()
            .freebusy()
            .query(
                body={
                    "timeMin": start.astimezone(timezone.utc).isoformat(),
                    "timeMax": end.astimezone(timezone.utc).isoformat(),
                    "items": [{"id": "primary"}],
                }
            )
            .execute()
        )
        busy = resp.get("calendars", {}).get("primary", {}).get("busy", [])
        out: list[tuple[datetime, datetime]] = []
        for b in busy:
            out.append(
                (
                    datetime.fromisoformat(b["start"].replace("Z", "+00:00")),
                    datetime.fromisoformat(b["end"].replace("Z", "+00:00")),
                )
            )
        return out

    def find_free_slots(
        self, duration_min: int = 60, days_ahead: int = 10, max_slots: int = 5
    ) -> list[dict]:
        """Propose up to max_slots free slots within work hours (Mon–Fri, local tz)."""
        duration = timedelta(minutes=max(15, min(duration_min, 480)))
        now = datetime.now(_TZ)
        window_start = now + timedelta(hours=1)  # don't propose the immediate next minutes
        window_end = now + timedelta(days=days_ahead)
        busy = self._busy_intervals(window_start, window_end)

        slots: list[dict] = []
        day = window_start.date()
        while day <= window_end.date() and len(slots) < max_slots:
            if datetime.combine(day, _WORK_START).weekday() < 5:  # Mon–Fri
                cursor = datetime.combine(day, _WORK_START, tzinfo=_TZ)
                day_end = datetime.combine(day, _WORK_END, tzinfo=_TZ)
                if cursor < window_start:
                    cursor = window_start.replace(second=0, microsecond=0)
                while cursor + duration <= day_end and len(slots) < max_slots:
                    cand_start, cand_end = cursor, cursor + duration
                    overlap = any(bs < cand_end and cand_start < be for bs, be in busy)
                    if not overlap:
                        slots.append(
                            {
                                "start": cand_start.isoformat(),
                                "end": cand_end.isoformat(),
                                "label": cand_start.strftime("%a %d %b, %H:%M"),
                            }
                        )
                        cursor = cand_end
                    else:
                        cursor += timedelta(minutes=30)
            day += timedelta(days=1)
        return slots

    # ── Write: create event (human-confirmed) ───────────────
    def create_event(
        self,
        *,
        summary: str,
        start_iso: str,
        end_iso: str | None = None,
        duration_min: int = 60,
        description: str | None = None,
        attendees: list[str] | None = None,
        send_updates: str = "none",
    ) -> dict:
        """Create a Calendar event. send_updates: 'all' emails invites, 'none' silent."""
        start_dt = datetime.fromisoformat(start_iso)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=_TZ)
        if end_iso:
            end_dt = datetime.fromisoformat(end_iso)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=_TZ)
        else:
            end_dt = start_dt + timedelta(minutes=max(15, duration_min))

        body: dict = {
            "summary": summary[:500],
            "description": description or "Creado desde Chatita Mail",
            "start": {"dateTime": start_dt.isoformat()},
            "end": {"dateTime": end_dt.isoformat()},
        }
        if attendees:
            body["attendees"] = [{"email": a} for a in attendees if a]

        ev = (
            self._service()
            .events()
            .insert(calendarId="primary", body=body, sendUpdates=send_updates)
            .execute()
        )
        return {
            "id": ev.get("id"),
            "link": ev.get("htmlLink"),
            "start": ev.get("start", {}).get("dateTime"),
            "end": ev.get("end", {}).get("dateTime"),
            "status": ev.get("status"),
            "invites_sent": send_updates == "all",
        }
