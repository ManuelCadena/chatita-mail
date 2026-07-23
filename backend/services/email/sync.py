"""
Chatita Mail v3.0 - Gmail sync service.

Pulls recent emails from Gmail (via GmailConnector), upserts them into the
unified `emails` table (idempotent by provider_message_id), and optionally
runs the full triage pipeline (classification + security + auto-actions).
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.entities import AccountProvider, Email, EmailAccount
from backend.services.email.gmail_connector import GmailConnector, NormalizedEmail
from backend.services.triage import TriageService

logger = logging.getLogger("chatita_mail.sync")


class GmailSyncService:
    def __init__(
        self,
        connector: GmailConnector | None = None,
        triage: TriageService | None = None,
    ) -> None:
        self.connector = connector or GmailConnector()
        self.triage = triage or TriageService()

    async def _get_or_create_account(
        self, session: AsyncSession, email_address: str
    ) -> EmailAccount:
        account = await session.scalar(
            select(EmailAccount).where(EmailAccount.email_address == email_address)
        )
        if account:
            return account
        account = EmailAccount(
            provider=AccountProvider.GMAIL,
            email_address=email_address,
            display_name=email_address,
        )
        session.add(account)
        await session.flush()
        return account

    async def _upsert_email(
        self, session: AsyncSession, account: EmailAccount, ne: NormalizedEmail
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

        from datetime import datetime

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

    async def sync(
        self,
        session: AsyncSession,
        max_results: int = 10,
        unread_only: bool = False,
        run_triage: bool = True,
    ) -> dict:
        """Pull -> upsert -> (optionally) triage. Returns a summary."""
        normalized = self.connector.list_inbox(
            max_results=max_results, unread_only=unread_only
        )
        if not normalized:
            return {"fetched": 0, "created": 0, "triaged": 0, "results": []}

        mailbox = self.connector.subject
        account = await self._get_or_create_account(session, mailbox)

        created = 0
        triaged = 0
        results: list[dict] = []

        for ne in normalized:
            email, was_created = await self._upsert_email(session, account, ne)
            created += int(was_created)

            item = {
                "email_id": email.id,
                "from": ne.from_address,
                "subject": ne.subject,
                "created": was_created,
            }

            if run_triage:
                try:
                    outcome = await self.triage.triage_email(session, email, auto_actions=True)
                    item.update(
                        {
                            "category": outcome.category.value,
                            "confidence": outcome.confidence,
                            "stage": outcome.stage,
                            "risk_level": outcome.risk_level.value,
                            "risk_score": outcome.risk_score,
                            "status": outcome.status.value,
                            "actions": outcome.actions,
                        }
                    )
                    triaged += 1
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Triage failed for %s: %s", email.id, exc)
                    item["triage_error"] = str(exc)

            results.append(item)

        return {
            "mailbox": mailbox,
            "fetched": len(normalized),
            "created": created,
            "triaged": triaged,
            "results": results,
        }
