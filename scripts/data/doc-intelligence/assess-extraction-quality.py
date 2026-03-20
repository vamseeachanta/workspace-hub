#!/usr/bin/env python3
"""Assess deep extraction quality and generate a summary report.

Reads worked_examples.jsonl, applies use_as_test flag, and reports stats.

Usage:
    uv run --no-project python scripts/data/doc-intelligence/assess-extraction-quality.py --report
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))

from scripts.data.doc_intelligence.assess_extraction_quality import (
    assess_example,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assess worked example extraction quality.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=_project_root / "data" / "doc-intelligence" / "worked_examples.jsonl",
        help="Path to worked_examples.jsonl",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print quality report to stdout",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1

    records = []
    with open(args.input) as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    assessed = [assess_example(r) for r in records]

    if args.report:
        total = len(assessed)
        testable = sum(1 for r in assessed if r.get("use_as_test"))
        by_format = Counter(r.get("parser_format", "classifier") for r in assessed)
        by_domain = Counter(r.get("domain", "unknown") for r in assessed)

        print(f"Total examples:     {total}")
        print(f"use_as_test=True:   {testable}")
        print(f"use_as_test=False:  {total - testable}")
        print(f"\nBy parser format:")
        for fmt, count in sorted(by_format.items()):
            print(f"  {fmt}: {count}")
        print(f"\nBy domain:")
        for dom, count in sorted(by_domain.items()):
            print(f"  {dom}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
