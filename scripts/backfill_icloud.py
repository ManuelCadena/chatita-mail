"""
Chatita Mail v3.0 — iCloud INBOX backfill (resumable).

Streams the newest N messages from the iCloud INBOX (by IMAP sequence range,
newest first) and upserts them in bounded chunks — committing per chunk so the
job is resumable and memory stays flat even for large pulls (10k+).

Triage is intentionally OFF here (cost/latency). Run scripts/triage_pending.py
afterwards to classify everything that has no Classification yet.

The account's last_sync_at is anchored to *now* at the end, so the systemd
incremental timer (chatita-mail-icloud.timer) picks up anything newer.

Usage (on the server, inside the venv):
    python -m scripts.backfill_icloud --max 10000
    python -m scripts.backfill_icloud --max 10000 --batch 100
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, ".")

from backend.models.db import AsyncSessionLocal  # noqa: E402
from backend.models.entities import AccountProvider  # noqa: E402
from backend.services.email.icloud_connector import ICloudConnector  # noqa: E402
from backend.services.email.sync import (  # noqa: E402
    _get_or_create_account,
    _upsert_email,
)


async def _run(max_total: int, batch: int) -> int:
    conn = ICloudConnector()
    started = time.time()

    total = await asyncio.to_thread(conn.count_inbox)
    if total == 0:
        print("[icloud-backfill] INBOX empty or unreachable", flush=True)
        return 1
    want = min(max_total, total)
    start = total - want + 1
    # Newest-first sequence numbers: total, total-1, ..., start
    seqs = [str(i).encode() for i in range(total, start - 1, -1)]
    print(
        f"[icloud-backfill] inbox_total={total} pulling newest={want} "
        f"batch={batch} — starting…",
        flush=True,
    )

    created = 0
    seen = 0
    async with AsyncSessionLocal() as session:
        account = await _get_or_create_account(
            session, conn.username, AccountProvider.ICLOUD
        )
        account.sync_status = "running"
        await session.commit()

        try:
            for off in range(0, len(seqs), batch):
                chunk = seqs[off : off + batch]
                nes = await asyncio.to_thread(conn.fetch_seqs, chunk)
                for ne in nes:
                    _, was_created = await _upsert_email(session, account, ne)
                    created += int(was_created)
                    seen += 1
                await session.commit()
                rate = seen / max(time.time() - started, 1e-6)
                print(
                    f"[icloud-backfill] fetched={seen}/{want} created={created} "
                    f"elapsed={time.time() - started:.0f}s rate={rate:.1f}/s",
                    flush=True,
                )
        finally:
            account.last_sync_at = datetime.now(tz=timezone.utc)
            account.sync_status = "idle"
            await session.commit()

    print(
        f"[icloud-backfill] DONE fetched={seen} created={created} "
        f"in {time.time() - started:.0f}s",
        flush=True,
    )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Chatita Mail iCloud backfill (resumable)")
    ap.add_argument("--max", type=int, default=10000, dest="max_total", help="Newest N to pull")
    ap.add_argument("--batch", type=int, default=100, help="Messages per IMAP connection/commit")
    args = ap.parse_args()
    sys.exit(asyncio.run(_run(args.max_total, args.batch)))


if __name__ == "__main__":
    main()
