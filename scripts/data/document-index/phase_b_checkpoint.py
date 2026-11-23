#!/usr/bin/env python3
# ABOUTME: Phase B checkpoint reporter — computes extraction stats per batch (WRK-1188)
# ABOUTME: Reads summaries dir, reports discipline distribution, error rate, method breakdown

"""
Checkpoint reporting for Phase B extraction batches.

Usage:
    uv run --no-project python scripts/data/document-index/phase_b_checkpoint.py
    uv run --no-project python scripts/data/document-index/phase_b_checkpoint.py --source og_standards
    uv run --no-project python scripts/data/document-index/phase_b_checkpoint.py --label "phase-1a-api"
"""

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [checkpoint] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

HUB_ROOT = Path(__file__).resolve().parents[3]
SUMMARIES_DIR = HUB_ROOT / "data/document-index/summaries"
CHECKPOINTS_DIR = HUB_ROOT / "data/document-index/checkpoints"


def compute_checkpoint(
    summaries_dir: Path = SUMMARIES_DIR,
    source_filter: str | None = None,
) -> dict:
    """Scan summaries dir and compute extraction statistics.

    Args:
        summaries_dir: Path to directory containing <sha>.json files.
        source_filter: If set, only count summaries with this source value.

    Returns:
        Dict with total, discipline_distribution, other_rate_pct,
        method_breakdown, org_breakdown.
    """
    discipline_counts: Counter = Counter()
    method_counts: Counter = Counter()
    org_counts: Counter = Counter()
    total = 0

    if not summaries_dir.exists():
        return {
            "total": 0,
            "discipline_distribution": {},
            "other_rate_pct": 0.0,
            "method_breakdown": {},
            "org_breakdown": {},
        }

    for p in summaries_dir.iterdir():
        if p.suffix != ".json":
            continue
        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        # Apply source filter
        if source_filter and data.get("source") != source_filter:
            continue

        # Only count docs that have a discipline (have been classified)
        discipline = data.get("discipline")
        if not discipline:
            continue

        total += 1
        discipline_counts[discipline] += 1
        method_counts[data.get("extraction_method", "unknown")] += 1
        org_counts[data.get("org", "unknown")] += 1

    other_count = discipline_counts.get("other", 0)
    other_rate = (other_count / total * 100) if total > 0 else 0.0

    return {
        "total": total,
        "discipline_distribution": dict(discipline_counts),
        "other_rate_pct": round(other_rate, 1),
        "method_breakdown": dict(method_counts),
        "org_breakdown": dict(org_counts),
    }


def write_checkpoint(
    report: dict,
    checkpoints_dir: Path = CHECKPOINTS_DIR,
    label: str = "batch",
) -> Path:
    """Write checkpoint report as YAML file.

    Returns path to the written file.
    """
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"checkpoint-{label}-{stamp}.yaml"
    out_path = checkpoints_dir / filename

    output = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "label": label,
        **report,
    }
    out_path.write_text(yaml.dump(output, default_flow_style=False, sort_keys=False))
    logger.info("Checkpoint written: %s", out_path)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase B checkpoint reporter (WRK-1188)",
    )
    parser.add_argument(
        "--source", default=None,
        help="Filter by source (e.g. og_standards)",
    )
    parser.add_argument(
        "--label", default="batch",
        help="Label for checkpoint file name",
    )
    args = parser.parse_args()

    report = compute_checkpoint(
        summaries_dir=SUMMARIES_DIR,
        source_filter=args.source,
    )
    logger.info(
        "total=%d other_rate=%.1f%%",
        report["total"], report["other_rate_pct"],
    )
    for disc, count in sorted(
        report["discipline_distribution"].items(), key=lambda x: -x[1],
    ):
        logger.info("  %s: %d", disc, count)

    write_checkpoint(report, label=args.label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
