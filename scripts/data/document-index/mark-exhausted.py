#!/usr/bin/env python3
# ABOUTME: Mark a standards-transfer-ledger entry as exhausted (WRK-1113)
# ABOUTME: Sets exhausted=true, exhausted_at, absorbed_into for a given entry ID

"""
Mark a ledger entry as exhausted (all key content absorbed into codebase).

Usage:
    uv run --no-project python scripts/data/document-index/mark-exhausted.py <entry-id> <module-path>
    uv run --no-project python scripts/data/document-index/mark-exhausted.py <entry-id> <module-path> [<module-path2> ...]

Examples:
    uv run --no-project python scripts/data/document-index/mark-exhausted.py API-RP-1632 digitalmodel/src/digitalmodel/cathodic_protection/api_rp_1632.py
    uv run --no-project python scripts/data/document-index/mark-exhausted.py DNV-RP-B401 digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HUB_ROOT = Path(__file__).resolve().parents[3]
LEDGER = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"


def load_ledger() -> dict:
    if not LEDGER.exists():
        print(f"Ledger not found: {LEDGER}", file=sys.stderr)
        sys.exit(1)
    with open(LEDGER) as f:
        return yaml.safe_load(f)


def save_ledger(data: dict) -> None:
    with open(LEDGER, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def find_entry(standards: list[dict], entry_id: str) -> dict | None:
    """Find entry by exact or partial case-insensitive ID match."""
    upper = entry_id.upper()
    # Exact match first
    for s in standards:
        if (s.get("id") or "").upper() == upper:
            return s
    # Partial match fallback
    matches = [s for s in standards if upper in (s.get("id") or "").upper()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Ambiguous ID '{entry_id}'. Matches:", file=sys.stderr)
        for m in matches:
            print(f"  {m['id']}", file=sys.stderr)
        sys.exit(1)
    return None


def mark_exhausted(entry_id: str, module_paths: list[str]) -> None:
    data = load_ledger()
    standards = data.get("standards", [])

    entry = find_entry(standards, entry_id)
    if entry is None:
        print(f"Entry not found: '{entry_id}'", file=sys.stderr)
        print("Run: uv run --no-project python scripts/data/document-index/query-ledger.py --id <partial>",
              file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry["exhausted"] = True
    entry["exhausted_at"] = now
    existing = entry.get("absorbed_into") or []
    for mp in module_paths:
        if mp not in existing:
            existing.append(mp)
    entry["absorbed_into"] = existing

    save_ledger(data)
    print(f"Marked exhausted: {entry['id']}")
    print(f"  exhausted_at:  {now}")
    print(f"  absorbed_into: {existing}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mark a ledger entry as exhausted")
    parser.add_argument("entry_id", help="Ledger entry ID (exact or partial)")
    parser.add_argument("module_paths", nargs="+", help="Module path(s) that absorbed the content")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without saving")
    args = parser.parse_args()

    if args.dry_run:
        data = load_ledger()
        entry = find_entry(data.get("standards", []), args.entry_id)
        if entry:
            print(f"Would mark exhausted: {entry['id']}")
            print(f"  absorbed_into: {args.module_paths}")
        else:
            print(f"Entry not found: {args.entry_id}")
        return

    mark_exhausted(args.entry_id, args.module_paths)


if __name__ == "__main__":
    main()
