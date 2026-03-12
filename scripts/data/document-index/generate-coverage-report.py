#!/usr/bin/env python3
# ABOUTME: Generate domain coverage report from standards-transfer-ledger (WRK-1113)
# ABOUTME: Writes docs/document-intelligence/domain-coverage.md

"""
Generates a Markdown domain coverage report from the standards-transfer-ledger.

Groups entries by domain and reports:
- Total entries per domain
- Done count
- Exhausted count
- Gap count

Usage:
    uv run --no-project python scripts/data/document-index/generate-coverage-report.py
    uv run --no-project python scripts/data/document-index/generate-coverage-report.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

HUB_ROOT = Path(__file__).resolve().parents[3]
LEDGER = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"
OUTPUT = HUB_ROOT / "docs/document-intelligence/domain-coverage.md"


def load_ledger() -> list[dict]:
    if not LEDGER.exists():
        print(f"Ledger not found: {LEDGER}", file=sys.stderr)
        sys.exit(1)
    with open(LEDGER) as f:
        data = yaml.safe_load(f)
    return data.get("standards", [])


def compute_domain_stats(standards: list[dict]) -> dict[str, dict]:
    """Group standards by domain and compute counts."""
    stats: dict[str, dict] = defaultdict(lambda: {
        "total": 0, "done": 0, "exhausted": 0, "gap": 0,
        "wrk_captured": 0, "in_progress": 0, "reference": 0,
    })
    for s in standards:
        domain = (s.get("domain") or "other").strip() or "other"
        st = stats[domain]
        st["total"] += 1
        status = s.get("status", "gap")
        if status in st:
            st[status] += 1
        if s.get("exhausted"):
            st["exhausted"] += 1
    return dict(stats)


def render_report(stats: dict[str, dict], generated_at: str) -> str:
    """Render the Markdown coverage report."""
    lines = [
        "# Document Intelligence — Domain Coverage Report",
        "",
        f"> Generated: {generated_at}",
        "> Source: `data/document-index/standards-transfer-ledger.yaml`",
        "> Re-generate: `uv run --no-project python scripts/data/document-index/generate-coverage-report.py`",
        "",
        "## Summary by Domain",
        "",
        "| Domain | Total | Done | Exhausted | WRK Captured | Gap |",
        "|--------|------:|-----:|----------:|-------------:|----:|",
    ]

    # Sort by total descending
    for domain, st in sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True):
        lines.append(
            f"| {domain} "
            f"| {st['total']} "
            f"| {st['done']} "
            f"| {st['exhausted']} "
            f"| {st['wrk_captured']} "
            f"| {st['gap']} |"
        )

    # Totals row
    total = sum(s["total"] for s in stats.values())
    done = sum(s["done"] for s in stats.values())
    exhausted = sum(s["exhausted"] for s in stats.values())
    wrk = sum(s["wrk_captured"] for s in stats.values())
    gap = sum(s["gap"] for s in stats.values())
    lines.append(
        f"| **TOTAL** | **{total}** | **{done}** | **{exhausted}** | **{wrk}** | **{gap}** |"
    )

    lines += [
        "",
        "## Column Definitions",
        "",
        "| Column | Meaning |",
        "|--------|---------|",
        "| Total | All entries in this domain |",
        "| Done | Implemented in codebase (status=done) |",
        "| Exhausted | All key content absorbed; source doc no longer needed |",
        "| WRK Captured | Tracked in a WRK item (status=wrk_captured) |",
        "| Gap | Not yet implemented (status=gap) |",
        "",
        "## Exhausted Entries",
        "",
    ]

    # List exhausted entries
    # (This section will be populated once documents are absorbed)
    lines.append(
        "_No entries exhausted yet. Run mark-exhausted.py after absorbing document content._"
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate domain coverage report")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print report to stdout without writing file",
    )
    args = parser.parse_args()

    standards = load_ledger()
    stats = compute_domain_stats(standards)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = render_report(stats, generated_at=now)

    if args.dry_run:
        print(report)
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(report, encoding="utf-8")
    print(f"Written: {OUTPUT.relative_to(HUB_ROOT)}")
    print(f"  Domains: {len(stats)}")
    print(f"  Total entries: {sum(s['total'] for s in stats.values())}")


if __name__ == "__main__":
    main()
