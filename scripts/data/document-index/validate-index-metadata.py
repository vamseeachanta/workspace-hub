#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Regression guard for data/document-index/index.jsonl (#1878).

Exits non-zero if the index's content_type / summary_done coverage drops below
configurable thresholds. Intended for wiring into CI or pre-commit after one
clean post-enrichment run.

Exit codes:
    0 — index passes all thresholds
    1 — index fails at least one threshold (or is empty)
    2 — usage error (argparse default)

Thresholds (CLI-overridable):
    --content-type-max-missing   0.10   (reject if >10% records lack the field)
    --content-type-min-non-other 0.90   (reject if <90% classified as non-`other`)
    --summary-done-min           0.55   (reject if <55% records are summary_done=True)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--content-type-max-missing", type=float, default=0.10)
    p.add_argument("--content-type-min-non-other", type=float, default=0.90)
    p.add_argument("--summary-done-min", type=float, default=0.55)
    return p.parse_args(argv)


def validate(
    *,
    index_path: Path,
    max_missing: float,
    min_non_other: float,
    min_summary_done: float,
) -> tuple[int, list[str]]:
    """Return (exit_code, messages)."""
    records: list[dict] = []
    with open(index_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    msgs: list[str] = []
    if not records:
        return 1, ["index is empty — refusing to pass"]

    total = len(records)
    missing_ct = sum(1 for r in records if r.get("content_type") is None)
    non_other_ct = sum(
        1 for r in records if r.get("content_type") not in (None, "other")
    )
    summary_done_true = sum(1 for r in records if r.get("summary_done") is True)

    missing_rate = missing_ct / total
    non_other_rate = non_other_ct / total
    summary_done_rate = summary_done_true / total

    if missing_rate > max_missing:
        msgs.append(
            f"FAIL: {missing_ct}/{total} records have content_type absent/null "
            f"({100*missing_rate:.1f}% > {100*max_missing:.1f}%)"
        )
    if non_other_rate < min_non_other:
        msgs.append(
            f"FAIL: only {non_other_ct}/{total} records have content_type != 'other' "
            f"({100*non_other_rate:.1f}% < {100*min_non_other:.1f}%)"
        )
    if summary_done_rate < min_summary_done:
        msgs.append(
            f"FAIL: only {summary_done_true}/{total} records have summary_done=True "
            f"({100*summary_done_rate:.1f}% < {100*min_summary_done:.1f}%)"
        )

    if msgs:
        return 1, msgs
    return 0, [
        f"PASS: {total} records; content_type missing={100*missing_rate:.1f}%, "
        f"non-other={100*non_other_rate:.1f}%, summary_done={100*summary_done_rate:.1f}%"
    ]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    code, msgs = validate(
        index_path=args.index,
        max_missing=args.content_type_max_missing,
        min_non_other=args.content_type_min_non_other,
        min_summary_done=args.summary_done_min,
    )
    for m in msgs:
        print(m, file=sys.stdout if code == 0 else sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
