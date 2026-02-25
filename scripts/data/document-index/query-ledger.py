#!/usr/bin/env python3
# ABOUTME: Query the standards transfer ledger for implementation status (WRK-606)
# ABOUTME: Filters by domain, status, org, repo, or specific standard ID

"""
Usage:
    python scripts/data/document-index/query-ledger.py --domain pipeline
    python scripts/data/document-index/query-ledger.py --status gap
    python scripts/data/document-index/query-ledger.py --id "API-RP-1111"
    python scripts/data/document-index/query-ledger.py --repo digitalmodel
    python scripts/data/document-index/query-ledger.py --org DNV --status gap
    python scripts/data/document-index/query-ledger.py --status gap --domain pipeline
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HUB_ROOT = Path(__file__).resolve().parents[3]
LEDGER = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"

STATUS_COLOUR = {
    "gap":          "\033[91m",   # red
    "wrk_captured": "\033[93m",   # yellow
    "in_progress":  "\033[94m",   # blue
    "done":         "\033[92m",   # green
    "reference":    "\033[90m",   # grey
    "deferred":     "\033[95m",   # magenta
}
RESET = "\033[0m"


def load_ledger() -> list[dict]:
    if not LEDGER.exists():
        print(f"Ledger not found: {LEDGER}", file=sys.stderr)
        print("Run: uv run --no-project python scripts/data/document-index/build-ledger.py",
              file=sys.stderr)
        sys.exit(1)
    with open(LEDGER) as f:
        data = yaml.safe_load(f)
    return data.get("standards", [])


def print_summary(standards: list[dict]) -> None:
    from collections import Counter
    counts = Counter(s.get("status", "gap") for s in standards)
    print(f"\nFound {len(standards)} standards")
    for k, v in sorted(counts.items()):
        col = STATUS_COLOUR.get(k, "")
        print(f"  {col}{k:15}{RESET} {v:>4}")


def print_table(standards: list[dict], verbose: bool = False) -> None:
    if not standards:
        print("No results.")
        return

    w_id, w_dom, w_st, w_wrk = 30, 20, 14, 10
    header = (f"{'ID':{w_id}} {'DOMAIN':{w_dom}} {'STATUS':{w_st}} "
              f"{'WRK':{w_wrk}} TITLE")
    print()
    print(header)
    print("-" * len(header))

    for s in standards:
        sid = (s.get("id") or "")[:w_id]
        dom = (s.get("domain") or "")[:w_dom]
        st = s.get("status", "gap")
        col = STATUS_COLOUR.get(st, "")
        wrk = (s.get("wrk_id") or "-")[:w_wrk]
        title = (s.get("title") or "")[:55]
        print(f"{sid:{w_id}} {dom:{w_dom}} {col}{st:{w_st}}{RESET} {wrk:{w_wrk}} {title}")

        if verbose:
            if s.get("doc_path"):
                print(f"  {'doc':>6}: {s['doc_path']}")
            if s.get("repo"):
                print(f"  {'repo':>6}: {s['repo']}")
            if s.get("modules"):
                print(f"  {'modules':>6}: {', '.join(s['modules'])}")
            if s.get("notes"):
                print(f"  {'notes':>6}: {s['notes'][:100]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Query standards transfer ledger")
    parser.add_argument("--domain",  help="Filter by domain (e.g. pipeline, structural)")
    parser.add_argument("--status",  help="Filter by status (gap|wrk_captured|done|reference|deferred)")
    parser.add_argument("--id",      help="Find a specific standard by ID (partial match)")
    parser.add_argument("--repo",    help="Filter by target repo (e.g. digitalmodel)")
    parser.add_argument("--org",     help="Filter by organisation (DNV, API, ASTM, ISO…)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show doc_path and notes")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary counts only")
    args = parser.parse_args()

    standards = load_ledger()

    if args.domain:
        standards = [s for s in standards if args.domain.lower() in (s.get("domain") or "").lower()]
    if args.status:
        standards = [s for s in standards if s.get("status") == args.status]
    if args.id:
        standards = [s for s in standards if args.id.upper() in (s.get("id") or "").upper()]
    if args.repo:
        standards = [s for s in standards if args.repo.lower() in (s.get("repo") or "").lower()]
    if args.org:
        standards = [s for s in standards if args.org.upper() in (s.get("org") or "").upper()]

    if args.summary:
        print_summary(standards)
    else:
        print_table(standards, verbose=args.verbose)
        print_summary(standards)


if __name__ == "__main__":
    main()
