#!/usr/bin/env python3
# ABOUTME: Phase 3b — compare ASTM deterministic vs LLM discipline for accuracy (WRK-1188)
# ABOUTME: Run AFTER LLM batch on 100 random ASTM docs; reports agreement rate

"""
ASTM deterministic classifier validation.

After running the LLM on a random 100-doc ASTM sample, this script
compares the deterministic discipline against the LLM discipline.

Usage:
    1. Run deterministic classifier first (phase_b_astm_classifier.py)
    2. Run LLM on 100 random ASTM docs:
       bash scripts/data/document-index/launch-batch.sh 2 og_standards ASTM
       (with --limit 50 per shard in the worker)
    3. Run this script to compare:
       uv run --no-project python scripts/data/document-index/phase-b-astm-validate.py
"""

import argparse
import json
import logging
import random
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [validate] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

HUB_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path("/mnt/ace/O&G-Standards/_inventory.db")
SUMMARIES_DIR = HUB_ROOT / "data/document-index/summaries"


def load_astm_hashes(limit: int = 0) -> list[str]:
    """Load content_hash values for non-duplicate ASTM docs."""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    rows = conn.execute("""
        SELECT d.content_hash
        FROM documents d
        WHERE d.is_duplicate = 0
          AND d.organization = 'ASTM'
          AND d.content_hash IS NOT NULL
        ORDER BY d.id
    """).fetchall()
    conn.close()
    hashes = [r[0] for r in rows if r[0]]
    if limit:
        random.seed(42)  # deterministic sample
        hashes = random.sample(hashes, min(limit, len(hashes)))
    return hashes


def compare_disciplines(
    hashes: list[str],
    summaries_dir: Path = SUMMARIES_DIR,
) -> dict:
    """Compare deterministic vs LLM discipline for given hashes.

    Returns stats dict with agreement count, disagreement details, etc.
    """
    agree = 0
    disagree = 0
    no_llm = 0
    disagreements = []

    for sha in hashes:
        p = summaries_dir / f"{sha}.json"
        if not p.exists():
            no_llm += 1
            continue

        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            no_llm += 1
            continue

        det_disc = data.get("discipline")
        llm_disc = data.get("llm_discipline")

        if not llm_disc:
            no_llm += 1
            continue

        if det_disc == llm_disc:
            agree += 1
        else:
            disagree += 1
            disagreements.append({
                "sha": sha,
                "deterministic": det_disc,
                "llm": llm_disc,
                "title": data.get("title", ""),
            })

    total_compared = agree + disagree
    accuracy = (agree / total_compared * 100) if total_compared > 0 else 0.0

    return {
        "total_hashes": len(hashes),
        "compared": total_compared,
        "agree": agree,
        "disagree": disagree,
        "no_llm_result": no_llm,
        "accuracy_pct": round(accuracy, 1),
        "disagreements": disagreements,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ASTM deterministic vs LLM validation (WRK-1188 Phase 3b)",
    )
    parser.add_argument(
        "--sample", type=int, default=100,
        help="Number of docs to sample (0=all with LLM results)",
    )
    args = parser.parse_args()

    hashes = load_astm_hashes(limit=args.sample)
    logger.info("Sampled %d ASTM hashes", len(hashes))

    result = compare_disciplines(hashes)
    logger.info(
        "Compared %d docs: %d agree, %d disagree → %.1f%% accuracy",
        result["compared"], result["agree"], result["disagree"],
        result["accuracy_pct"],
    )
    if result["no_llm_result"]:
        logger.info(
            "%d docs had no LLM result (run LLM batch first)",
            result["no_llm_result"],
        )
    if result["disagreements"]:
        logger.info("Disagreements:")
        for d in result["disagreements"][:20]:
            logger.info(
                "  %s: det=%s llm=%s title=%s",
                d["sha"][:12], d["deterministic"], d["llm"], d["title"][:50],
            )

    if result["accuracy_pct"] >= 90:
        logger.info("PASS: accuracy >= 90%% — trust deterministic results")
    elif result["compared"] > 0:
        logger.warning(
            "FAIL: accuracy %.1f%% < 90%% — expand LLM coverage",
            result["accuracy_pct"],
        )
    else:
        logger.warning("No comparisons possible — run LLM batch on ASTM sample first")

    return 0


if __name__ == "__main__":
    sys.exit(main())
