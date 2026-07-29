"""
Chatita Mail — resumable mass RE-CLASSIFY (post no-sql-injection fix).

Re-runs ONLY the classifier (lexical prefilter + AION LLM stage-2) over the
entire mailbox and updates the Classification row. It deliberately does NOT
run the full triage pipeline, so it never re-fires side effects on historical
mail (no Telegram alerts, no unsubscribe HTTP calls, no phishing re-analysis)
and wastes no AION calls on the (currently 404) opencorporates tool.

Rate-limit strategy (AION Brain enforces 60 req/min PER userId):
  - aion.orchestrate is monkeypatched to (a) round-robin user_id across SHARDS
    synthetic batch identities so we get SHARDS separate 60/min buckets, and
    (b) pass every call through a smooth global limiter (~RATE_PER_MIN total).
  - This keeps us well under each per-user cap and, crucially, uses batch
    identities distinct from Manny's own userId, so his live AION usage is
    unaffected.

Design:
  - Snapshots ALL email ids once into retriage_ids.txt (stable, resumable).
  - Checkpoints progress index in retriage_progress.json every CHECKPOINT emails.
  - Each email uses its own AsyncSession (async sessions are not concurrency-safe).
  - Logs per-batch quality (llm vs lexical vs fallback) to stdout / nohup log.

Run:   nohup venv/bin/python scripts/retriage_all.py > scripts/retriage.log 2>&1 &
Stop:  pkill -f retriage_all.py     (safe: resumes from last checkpoint)
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import os
import sys
import time
from pathlib import Path

# Ensure the project root (parent of scripts/) is importable when run as a file.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from backend.ai.aion_client import aion
from backend.ai.classifier import EmailClassifier
from backend.models.db import AsyncSessionLocal
from backend.models.entities import Classification, Email

CONCURRENCY = int(os.getenv("RETRIAGE_CONCURRENCY", "8"))
SHARDS = int(os.getenv("RETRIAGE_SHARDS", "5"))          # separate 60/min buckets
RATE_PER_MIN = int(os.getenv("RETRIAGE_RATE_PER_MIN", "250"))  # global smoothing (<SHARDS*60)
CHECKPOINT = 50
HERE = Path(__file__).resolve().parent
IDS_FILE = HERE / "retriage_ids.txt"
PROGRESS_FILE = HERE / "retriage_progress.json"
LOCK_FILE = HERE / "retriage.lock"
_lock_fh = None  # kept open for the process lifetime to hold the flock


def _acquire_singleton_lock() -> bool:
    """Exclusive non-blocking flock so at most ONE batch runs at a time.
    Returns False (and the caller exits) if another instance already holds it.
    """
    global _lock_fh
    _lock_fh = open(LOCK_FILE, "w")
    try:
        fcntl.flock(_lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fh.write(str(os.getpid()))
        _lock_fh.flush()
        return True
    except BlockingIOError:
        return False

_classifier = EmailClassifier()
_sem = asyncio.Semaphore(CONCURRENCY)

# Live counters
_stats = {"done": 0, "llm": 0, "lexical": 0, "fallback": 0, "errors": 0}


# ── AION throttle + per-user sharding (monkeypatch the shared singleton) ──
class _SmoothLimiter:
    """Global leaky-bucket: emits at most RATE_PER_MIN calls/min, evenly spaced."""

    def __init__(self, per_min: int) -> None:
        self._interval = 60.0 / max(1, per_min)
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait = self._next - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._next = max(now, self._next) + self._interval


_limiter = _SmoothLimiter(RATE_PER_MIN)
_shard_counter = {"n": 0}
_orig_orchestrate = aion.orchestrate


async def _throttled_orchestrate(prompt, task_type="medium", **kwargs):
    await _limiter.acquire()
    n = _shard_counter["n"] % SHARDS
    _shard_counter["n"] += 1
    kwargs.setdefault("user_id", f"chatita-mail-rt{n}")
    return await _orig_orchestrate(prompt, task_type=task_type, **kwargs)


aion.orchestrate = _throttled_orchestrate  # type: ignore[assignment]


async def _snapshot_ids() -> list[str]:
    """Build (once) a stable ordered list of all email ids."""
    if IDS_FILE.exists():
        return IDS_FILE.read_text().splitlines()
    async with AsyncSessionLocal() as s:
        rows = (
            await s.scalars(
                select(Email.id).order_by(Email.received_at.desc().nullslast())
            )
        ).all()
    IDS_FILE.write_text("\n".join(rows))
    return list(rows)


def _load_index() -> int:
    if PROGRESS_FILE.exists():
        try:
            return int(json.loads(PROGRESS_FILE.read_text()).get("index", 0))
        except Exception:  # noqa: BLE001
            return 0
    return 0


def _save_index(index: int) -> None:
    PROGRESS_FILE.write_text(json.dumps({"index": index, "stats": _stats, "ts": time.time()}))


def _is_fallback(cls: Classification | None) -> bool:
    if cls is None:
        return True
    reason = (cls.reasoning or "").lower()
    return "could not parse" in reason or (cls.confidence == 0.5 and cls.stage == "llm")


async def _retriage_one(email_id: str) -> None:
    async with _sem:
        try:
            async with AsyncSessionLocal() as session:
                email = await session.scalar(select(Email).where(Email.id == email_id))
                if not email:
                    return
                cls = await _classifier.classify(
                    from_address=email.from_address,
                    from_name=email.from_name,
                    subject=email.subject,
                    body_text=email.body_text,
                )
                row = await session.scalar(
                    select(Classification).where(Classification.email_id == email_id)
                )
                if row is None:
                    row = Classification(email_id=email_id)
                    session.add(row)
                row.category = cls.category
                row.confidence = cls.confidence
                row.stage = cls.stage
                row.reasoning = cls.reasoning
                row.is_newsletter = cls.is_newsletter
                row.unsubscribe_url = cls.unsubscribe_url
                await session.commit()
                if cls.stage == "lexical":
                    _stats["lexical"] += 1
                elif _is_fallback(row):
                    _stats["fallback"] += 1
                else:
                    _stats["llm"] += 1
        except Exception as exc:  # noqa: BLE001
            _stats["errors"] += 1
            print(f"  ERR {email_id}: {exc}", flush=True)
        finally:
            _stats["done"] += 1


async def main() -> None:
    if not _acquire_singleton_lock():
        print("[retriage] another instance is already running (lock held) -> exit", flush=True)
        return
    ids = await _snapshot_ids()
    start = _load_index()
    total = len(ids)
    print(
        f"[retriage] total={total} start_index={start} concurrency={CONCURRENCY} "
        f"shards={SHARDS} rate_per_min={RATE_PER_MIN}",
        flush=True,
    )
    t0 = time.time()
    batch: list[asyncio.Task] = []
    for i in range(start, total):
        batch.append(asyncio.create_task(_retriage_one(ids[i])))
        if len(batch) >= CONCURRENCY:
            await asyncio.gather(*batch)
            batch = []
            if _stats["done"] % CHECKPOINT < CONCURRENCY:
                _save_index(i + 1)
                rate = _stats["done"] / max(1e-9, time.time() - t0)
                eta = (total - (i + 1)) / max(1e-9, rate) / 60
                print(
                    f"[retriage] idx={i+1}/{total} done={_stats['done']} "
                    f"llm={_stats['llm']} lexical={_stats['lexical']} "
                    f"fallback={_stats['fallback']} err={_stats['errors']} "
                    f"rate={rate:.1f}/s eta={eta:.0f}min",
                    flush=True,
                )
    if batch:
        await asyncio.gather(*batch)
    _save_index(total)
    print(f"[retriage] DONE {json.dumps(_stats)} elapsed={(time.time()-t0)/60:.1f}min", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
