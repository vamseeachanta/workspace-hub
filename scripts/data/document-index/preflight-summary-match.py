#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Pre-flight summary-file match-rate reconciliation for #1878.

Samples N records from index.jsonl, attempts the same four-pattern lookup the
enrichment script will use, and reports the match rate per filename pattern.

Exits 1 if the overall match rate falls below (expected_rate - safety_margin).
Run before a full enrichment so a bad mount / bad hash scheme / stale summary
dir is caught before 649K records are touched.

Example:
    uv run --no-project python scripts/data/document-index/preflight-summary-match.py \
        --expected-rate 0.837 --safety-margin 0.05 --sample-size 1000
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

PATTERNS = ("prefixed", "bare_stripped", "path_fallback")


def _classify_match(record: dict, summaries_dir: Path) -> str | None:
    """Return the first pattern name that resolves, or None if no match."""
    ch = record.get("content_hash") or None
    path = record["path"]
    path_key = hashlib.sha256(path.encode()).hexdigest()[:16]

    if ch:
        if (summaries_dir / f"{ch}.json").exists():
            return "prefixed"
        if ":" in ch:
            _, bare = ch.split(":", 1)
            if (summaries_dir / f"{bare}.json").exists():
                return "bare_stripped"
    if (summaries_dir / f"{path_key}.json").exists():
        return "path_fallback"
    return None


def run_preflight(
    *,
    index_path: Path,
    summaries_dir: Path,
    sample_size: int,
    expected_rate: float,
    safety_margin: float,
    seed: int | None,
) -> tuple[int, dict]:
    records: list[dict] = []
    with open(index_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    if not records:
        return 1, {"error": "index empty"}

    rng = random.Random(seed)
    n = min(sample_size, len(records))
    sample = rng.sample(records, n) if len(records) > n else records[:]

    per_pattern: dict[str, int] = {p: 0 for p in PATTERNS}
    matches = 0
    for r in sample:
        p = _classify_match(r, summaries_dir)
        if p is not None:
            per_pattern[p] += 1
            matches += 1

    rate = matches / n
    floor = expected_rate - safety_margin
    ok = rate >= floor

    stats = {
        "sample_size": n,
        "matches": matches,
        "match_rate": rate,
        "floor": floor,
        "per_pattern": per_pattern,
    }
    return (0 if ok else 1), stats


def _print_report(stats: dict, ok: bool) -> None:
    print(
        f"Preflight: {stats['matches']}/{stats['sample_size']} "
        f"({100*stats['match_rate']:.1f}%) match rate "
        f"(floor {100*stats['floor']:.1f}%) — {'PASS' if ok else 'FAIL'}"
    )
    for p in PATTERNS:
        print(f"  {p}: {stats['per_pattern'][p]}")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--summaries-dir", type=Path, required=True)
    p.add_argument("--sample-size", type=int, default=1000)
    p.add_argument("--expected-rate", type=float, default=0.837)
    p.add_argument("--safety-margin", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    code, stats = run_preflight(
        index_path=args.index,
        summaries_dir=args.summaries_dir,
        sample_size=args.sample_size,
        expected_rate=args.expected_rate,
        safety_margin=args.safety_margin,
        seed=args.seed,
    )
    if "error" in stats:
        print(stats["error"], file=sys.stderr)
        return code
    _print_report(stats, ok=(code == 0))
    return code


if __name__ == "__main__":
    sys.exit(main())
