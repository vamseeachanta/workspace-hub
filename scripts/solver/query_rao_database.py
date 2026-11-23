#!/usr/bin/env python3
"""Query the RAODatabase populated by post-process-hook.py.

ABOUTME: CLI to inspect the Parquet-backed RAO database at data/rao_database.parquet.
Lists entries, shows metadata, and queries by hull parameters.

Usage:
    uv run python scripts/solver/query_rao_database.py               # list all
    uv run python scripts/solver/query_rao_database.py --id <id>     # show one entry
    uv run python scripts/solver/query_rao_database.py --stats       # summary stats

Traceability: #1787
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAO_DB_PATH = REPO_ROOT / "data" / "rao_database.parquet"


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="query_rao_database",
        description="Query the RAO database.",
    )
    parser.add_argument("--db", type=Path, default=RAO_DB_PATH, help="Database path")
    parser.add_argument("--id", type=str, default=None, help="Show specific entry by variation_id")
    parser.add_argument("--stats", action="store_true", help="Show summary statistics")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"No RAO database found at {args.db}")
        print("Run post-process-hook.py on completed OrcaWave jobs to populate it.")
        return 1

    try:
        from digitalmodel.hydrodynamics.hull_library.rao_database import RAODatabase
    except ImportError:
        print("ERROR: digitalmodel package not available", file=sys.stderr)
        return 1

    db = RAODatabase()
    db.load_from_disk(args.db)
    entries = list(db.query({}))

    if args.id:
        try:
            entry = db.get_by_id(args.id)
        except KeyError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(f"Variation ID: {entry.variation_id}")
        print(f"Vessel name:  {entry.rao_data.vessel_name}")
        print(f"Frequencies:  {len(entry.rao_data.frequencies)} ({entry.rao_data.frequencies[0]:.4f} – {entry.rao_data.frequencies[-1]:.4f} rad/s)")
        print(f"Directions:   {len(entry.rao_data.directions)} ({entry.rao_data.directions[0]:.1f}° – {entry.rao_data.directions[-1]:.1f}°)")
        print(f"Amplitudes:   {entry.rao_data.amplitudes.shape}")
        print(f"Hull params:  {entry.hull_params}")
        print(f"Metadata:")
        for k, v in entry.metadata.items():
            print(f"  {k}: {v}")
        return 0

    if args.stats:
        print(f"RAO Database: {args.db}")
        print(f"Entries: {len(entries)}")
        params = db.list_parameters()
        if params:
            print(f"Hull parameters:")
            for k, vals in params.items():
                print(f"  {k}: {sorted(vals)}")
        print(f"\nEntries:")
        for e in entries:
            n_freq = len(e.rao_data.frequencies)
            n_dir = len(e.rao_data.directions)
            print(f"  {e.variation_id}: {e.rao_data.vessel_name} ({n_freq} freq × {n_dir} dir)")
        return 0

    # Default: list all
    print(f"RAO Database: {args.db} ({len(entries)} entries)")
    print()
    for e in entries:
        n_freq = len(e.rao_data.frequencies)
        n_dir = len(e.rao_data.directions)
        solver = e.metadata.get("solver", "?")
        desc = e.metadata.get("description", "")[:50]
        print(f"  {e.variation_id}")
        print(f"    vessel={e.rao_data.vessel_name}  {n_freq}freq × {n_dir}dir  solver={solver}")
        if desc:
            print(f"    {desc}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
