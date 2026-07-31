"""
Chatita Mail v3.0 — Embedding backfill.

Generates BGE-M3 embeddings for emails that don't yet have one and stores them
in the pgvector `embeddings.vector` column. Batched, resumable (skips emails
already embedded), and rate-limited so it can run in the background without
overwhelming a small instance or the HF Inference API.

Usage:
    python -m scripts.backfill_embeddings                 # all remaining
    python -m scripts.backfill_embeddings --limit 100     # validation run
    python -m scripts.backfill_embeddings --batch-size 16 --sleep 0.3
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import time

from sqlalchemy import text

from backend.models.db import AsyncSessionLocal
from backend.services.embeddings import EmbeddingService, build_email_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill_embeddings")


async def _fetch_batch(session, batch_size: int) -> list[dict]:
    """Return the next batch of emails lacking an embedding."""
    rows = (
        await session.execute(
            text(
                "SELECT e.id, e.subject, e.body_text, e.snippet "
                "FROM emails e "
                "LEFT JOIN embeddings emb ON emb.email_id = e.id "
                "WHERE emb.id IS NULL "
                "ORDER BY e.received_at DESC NULLS LAST "
                "LIMIT :n"
            ),
            {"n": batch_size},
        )
    ).all()
    return [
        {"id": str(r[0]), "subject": r[1], "body_text": r[2], "snippet": r[3]}
        for r in rows
    ]


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="Max emails to embed (0 = all)")
    ap.add_argument("--batch-size", type=int, default=16, help="Texts per HF request")
    ap.add_argument("--concurrency", type=int, default=4, help="Parallel HF requests")
    ap.add_argument("--sleep", type=float, default=0.2, help="Seconds between rounds")
    args = ap.parse_args()

    embedder = EmbeddingService()
    if not embedder.token:
        raise SystemExit("HF token not configured (settings.hf_token empty). Aborting.")

    done = 0
    failed = 0
    started = time.time()

    async def _embed_one(sub: list[dict]) -> tuple[list[dict], list[list[float]] | None]:
        texts = [build_email_text(b["subject"], b["body_text"], b["snippet"]) for b in sub]
        try:
            return sub, await embedder.embed_batch(texts)
        except Exception as exc:  # noqa: BLE001
            log.warning("Sub-batch embed failed (%d emails): %s", len(sub), exc)
            return sub, None

    while True:
        remaining = (args.limit - done) if args.limit else (args.batch_size * args.concurrency)
        if args.limit and remaining <= 0:
            break
        round_size = args.batch_size * args.concurrency
        if args.limit:
            round_size = min(round_size, remaining)

        async with AsyncSessionLocal() as session:
            batch = await _fetch_batch(session, round_size)
            if not batch:
                log.info("No more emails to embed. Stopping.")
                break

            # Split into sub-batches and embed them concurrently.
            subs = [batch[i : i + args.batch_size] for i in range(0, len(batch), args.batch_size)]
            results = await asyncio.gather(*[_embed_one(s) for s in subs])

            for sub, vectors in results:
                if vectors is None:
                    failed += len(sub)
                    continue
                for b, vec in zip(sub, vectors):
                    await embedder.store_embedding(session, b["id"], vec)
                done += len(sub)
            await session.commit()

        rate = done / max(1e-6, time.time() - started)
        log.info("Embedded %d (failed %d) · %.1f/s", done, failed, rate)
        await asyncio.sleep(args.sleep)

    log.info("DONE. Embedded=%d failed=%d in %.0fs", done, failed, time.time() - started)


if __name__ == "__main__":
    asyncio.run(main())
