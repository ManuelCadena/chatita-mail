"""
Chatita Mail v3.0 — Triage backfilled emails (resumable).

Classifies every email that has no Classification yet (2-stage: lexical
pre-filter → LLM for ambiguous cases) and applies auto-actions
(archive NOISE/SPAM, block dangerous, etc.). Newest-first.

Commits after EACH email, so the job is naturally resumable: already-
triaged emails gain a Classification row and are skipped on re-run.

Usage (on the server, inside the venv):
    python -m scripts.triage_pending                 # all pending
    python -m scripts.triage_pending --max 5000      # cap
    python -m scripts.triage_pending --batch 200     # fetch size
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time

sys.path.insert(0, ".")

from sqlalchemy import func, select  # noqa: E402

from backend.models.db import AsyncSessionLocal  # noqa: E402
from backend.models.entities import Classification, Email  # noqa: E402
from backend.services.triage import TriageService  # noqa: E402


def _pending_stmt(limit: int):
    return (
        select(Email)
        .outerjoin(Classification, Classification.email_id == Email.id)
        .where(Classification.id.is_(None))
        .order_by(Email.received_at.desc().nullslast())
        .limit(limit)
    )


async def _run(batch: int, max_total: int | None) -> int:
    svc = TriageService()
    done = 0
    errors = 0
    started = time.time()
    async with AsyncSessionLocal() as session:
        pending = await session.scalar(
            select(func.count(Email.id))
            .outerjoin(Classification, Classification.email_id == Email.id)
            .where(Classification.id.is_(None))
        )
        print(f"[triage] pending={pending} batch={batch} max={max_total} — starting…", flush=True)

        while True:
            if max_total is not None and done >= max_total:
                break
            emails = (await session.scalars(_pending_stmt(batch))).all()
            if not emails:
                break
            for email in emails:
                if max_total is not None and done >= max_total:
                    break
                try:
                    await svc.triage_email(session, email, auto_actions=True)
                    await session.commit()
                    done += 1
                except Exception as exc:  # noqa: BLE001
                    await session.rollback()
                    errors += 1
                    print(f"[triage] error on {email.id}: {exc}", flush=True)
            rate = done / max(time.time() - started, 1e-6)
            print(
                f"[triage] processed={done} errors={errors} "
                f"elapsed={time.time() - started:.0f}s rate={rate:.1f}/s",
                flush=True,
            )
    print(f"[triage] DONE processed={done} errors={errors} in {time.time() - started:.0f}s", flush=True)
    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description="Chatita Mail triage backfill (resumable)")
    ap.add_argument("--batch", type=int, default=100, help="Fetch size per DB round-trip")
    ap.add_argument("--max", type=int, default=None, dest="max_total", help="Cap emails to triage")
    args = ap.parse_args()
    errors = asyncio.run(_run(args.batch, args.max_total))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
