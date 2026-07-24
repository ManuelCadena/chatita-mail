"""
Chatita Mail v3.0 — Gmail full backfill (resumable).

Runs the entire mailbox ingest OUTSIDE the HTTP request path so large
mailboxes (e.g. 31k messages) don't hit request timeouts. Idempotent by
provider_message_id: re-running skips already-stored messages, so a
crashed/interrupted run can simply be restarted.

The backfill anchors the account's last_history_id BEFORE listing, so a
subsequent incremental sync (`/sync/gmail/incremental`) catches anything
that arrives during the backfill.

Usage (on the server, inside the venv):
    python -m scripts.backfill_gmail --scope inbox            # INBOX only
    python -m scripts.backfill_gmail --scope all              # ALL mail
    python -m scripts.backfill_gmail --scope inbox --max 5000 # cap
    python -m scripts.backfill_gmail --scope inbox --triage   # triage inline (slow)

Recommended for 31k: run WITHOUT --triage, then classify in batches via
`POST /api/inbox/triage/pending?limit=500` (repeat) or the same triage path.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time

# Ensure project root importable when run as a file
sys.path.insert(0, ".")

from backend.models.db import AsyncSessionLocal  # noqa: E402
from backend.services.email.sync import GmailSyncService  # noqa: E402


async def _run(scope: str, max_total: int | None, triage: bool, batch_size: int) -> int:
    query = "in:inbox" if scope == "inbox" else None
    label_ids = None if scope == "inbox" else []

    svc = GmailSyncService()
    started = time.time()
    print(
        f"[backfill] scope={scope} max_total={max_total} triage={triage} "
        f"batch_size={batch_size} — starting…",
        flush=True,
    )
    async with AsyncSessionLocal() as session:
        summary = await svc.full_sync(
            session,
            query=query,
            label_ids=label_ids,
            max_total=max_total,
            run_triage=triage,
            batch_size=batch_size,
        )
    elapsed = time.time() - started
    print(f"[backfill] done in {elapsed:.1f}s: {summary}", flush=True)
    return int(summary.get("failed", 0) or 0)


def main() -> None:
    ap = argparse.ArgumentParser(description="Chatita Mail Gmail backfill (resumable)")
    ap.add_argument("--scope", choices=["inbox", "all"], default="inbox")
    ap.add_argument("--max", type=int, default=None, dest="max_total",
                    help="Cap number of messages (default: every message)")
    ap.add_argument("--triage", action="store_true",
                    help="Run triage during backfill (slow/costly)")
    ap.add_argument("--batch-size", type=int, default=100,
                    help="Commit every N messages (default 100)")
    args = ap.parse_args()

    failed = asyncio.run(
        _run(args.scope, args.max_total, args.triage, args.batch_size)
    )
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
