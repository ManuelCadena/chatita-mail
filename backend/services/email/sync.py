"""
Chatita Mail v3.0 - Email sync services (Gmail + iCloud).

Both services:
  - Pull from their respective connectors
  - Upsert into the unified `emails` table (idempotent by provider_message_id)
  - Optionally run the full triage pipeline (classify + security + auto-actions)
  - Support incremental sync anchored on EmailAccount.last_sync_at
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.entities import AccountProvider, Email, EmailAccount
from backend.services.email.gmail_connector import GmailConnector, NormalizedEmail
from backend.services.email.icloud_connector import ICloudConnector
from backend.services.triage import TriageService

logger = logging.getLogger("chatita_mail.sync")


# ── Shared helpers ─────────────────────────────────────────


async def _get_or_create_account(
    session: AsyncSession,
    email_address: str,
    provider: AccountProvider,
) -> EmailAccount:
    account = await session.scalar(
        select(EmailAccount).where(EmailAccount.email_address == email_address)
    )
    if account:
        return account
    account = EmailAccount(
        provider=provider,
        email_address=email_address,
        display_name=email_address,
    )
    session.add(account)
    await session.flush()
    return account


async def _upsert_email(
    session: AsyncSession, account: EmailAccount, ne: NormalizedEmail
) -> tuple[Email, bool]:
    """Return (email, created). Idempotent by provider_message_id."""
    existing = await session.scalar(
        select(Email).where(
            Email.account_id == account.id,
            Email.provider_message_id == ne.provider_message_id,
        )
    )
    if existing:
        return existing, False

    received = None
    if ne.received_at:
        try:
            received = datetime.fromisoformat(ne.received_at)
        except ValueError:
            received = None

    email = Email(
        account_id=account.id,
        provider_message_id=ne.provider_message_id,
        thread_id=ne.thread_id,
        from_address=ne.from_address,
        from_name=ne.from_name,
        to_addresses=ne.to_addresses,
        cc_addresses=ne.cc_addresses,
        subject=ne.subject,
        body_text=ne.body_text,
        body_html=ne.body_html,
        snippet=ne.snippet or (ne.body_text or "")[:200],
        attachments=ne.attachments,
        received_at=received,
    )
    session.add(email)
    await session.flush()
    return email, True


async def _run_triage(
    triage: TriageService, session: AsyncSession, email: Email
) -> dict:
    try:
        outcome = await triage.triage_email(session, email, auto_actions=True)
        return {
            "category": outcome.category.value,
            "confidence": outcome.confidence,
            "stage": outcome.stage,
            "risk_level": outcome.risk_level.value,
            "risk_score": outcome.risk_score,
            "status": outcome.status.value,
            "actions": outcome.actions,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Triage failed for %s: %s", email.id, exc)
        return {"triage_error": str(exc)}


# ── Gmail ───────────────────────────────────────────────────


class GmailSyncService:
    def __init__(
        self,
        connector: GmailConnector | None = None,
        triage: TriageService | None = None,
    ) -> None:
        self.connector = connector or GmailConnector()
        self.triage = triage or TriageService()

    async def sync(
        self,
        session: AsyncSession,
        max_results: int = 10,
        unread_only: bool = False,
        run_triage: bool = True,
    ) -> dict:
        """Pull → upsert → (optionally) triage. Marks account last_sync_at."""
        normalized = self.connector.list_inbox(
            max_results=max_results, unread_only=unread_only
        )
        if not normalized:
            return {"fetched": 0, "created": 0, "triaged": 0, "results": []}

        mailbox = self.connector.subject
        account = await _get_or_create_account(session, mailbox, AccountProvider.GMAIL)

        created = 0
        triaged = 0
        results: list[dict] = []

        for ne in normalized:
            email, was_created = await _upsert_email(session, account, ne)
            created += int(was_created)
            item: dict = {
                "email_id": email.id,
                "from": ne.from_address,
                "subject": ne.subject,
                "created": was_created,
            }
            if run_triage:
                item.update(await _run_triage(self.triage, session, email))
                triaged += 1
            results.append(item)

        account.last_sync_at = datetime.now(tz=timezone.utc)
        return {
            "provider": "gmail",
            "mailbox": mailbox,
            "fetched": len(normalized),
            "created": created,
            "triaged": triaged,
            "results": results,
        }


# ── iCloud ──────────────────────────────────────────────────


class ICloudSyncService:
    """
    Incremental iCloud IMAP sync.

    On each call, fetches only messages received since the account's
    last_sync_at timestamp (EmailAccount.last_sync_at).  Falls back to
    `initial_lookback_days` for the first ever sync.
    """

    DEFAULT_LOOKBACK_DAYS = 7

    def __init__(
        self,
        connector: ICloudConnector | None = None,
        triage: TriageService | None = None,
        initial_lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> None:
        self.connector = connector or ICloudConnector()
        self.triage = triage or TriageService()
        self.initial_lookback_days = initial_lookback_days

    async def sync(
        self,
        session: AsyncSession,
        max_results: int = 50,
        run_triage: bool = True,
        force_full: bool = False,
    ) -> dict:
        """
        Incremental pull → upsert → triage.

        Args:
            max_results: max messages to pull per run (cap for safety).
            run_triage: run classification + security pipeline on new emails.
            force_full: ignore last_sync_at and pull max_results newest messages.
        """
        mailbox = self.connector.username
        account = await _get_or_create_account(session, mailbox, AccountProvider.ICLOUD)

        # Determine incremental anchor
        since_date: datetime | None = None
        if not force_full and account.last_sync_at:
            since_date = account.last_sync_at
        elif not force_full:
            since_date = datetime.now(tz=timezone.utc) - timedelta(
                days=self.initial_lookback_days
            )

        normalized = self.connector.list_inbox(
            max_results=max_results,
            unread_only=False,
            since_date=since_date,
        )
        if not normalized:
            account.last_sync_at = datetime.now(tz=timezone.utc)
            return {
                "provider": "icloud",
                "mailbox": mailbox,
                "fetched": 0,
                "created": 0,
                "triaged": 0,
                "since": since_date.isoformat() if since_date else None,
                "results": [],
            }

        created = 0
        triaged = 0
        results: list[dict] = []

        for ne in normalized:
            email, was_created = await _upsert_email(session, account, ne)
            created += int(was_created)
            item: dict = {
                "email_id": email.id,
                "from": ne.from_address,
                "subject": ne.subject,
                "created": was_created,
            }
            if run_triage and was_created:
                item.update(await _run_triage(self.triage, session, email))
                triaged += 1
            results.append(item)

        account.last_sync_at = datetime.now(tz=timezone.utc)
        return {
            "provider": "icloud",
            "mailbox": mailbox,
            "fetched": len(normalized),
            "created": created,
            "triaged": triaged,
            "since": since_date.isoformat() if since_date else None,
            "results": results,
        }
