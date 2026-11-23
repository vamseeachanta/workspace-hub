#!/usr/bin/env python3
# ABOUTME: Audit index-merged.jsonl for ghost entries (paths that no longer exist on disk)
# ABOUTME: Reports ghost count by source, writes clean index without ghosts

"""
Usage:
    python ghost-audit.py [--clean] [--output PATH]

Without --clean: report-only mode (counts ghosts by source).
With --clean: writes a ghost-free index to --output (default: index-clean.jsonl).
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
MERGED_INDEX = HUB_ROOT / "data" / "document-index" / "index-merged.jsonl"


def audit(index_path: Path, clean: bool = False, output_path: Path = None):
    total = 0
    ghost_count = 0
    live_count = 0
    api_count = 0
    ghost_by_source = Counter()
    live_by_source = Counter()
    ghost_samples = []  # first 10 ghost paths for inspection

    clean_records = []

    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            total += 1
            path = rec.get("path", "")
            source = rec.get("source", "unknown")

            # API metadata entries are virtual -- not filesystem paths
            if path.startswith("api://"):
                api_count += 1
                live_count += 1
                live_by_source[source] += 1
                if clean:
                    clean_records.append(rec)
                continue

            # Check if file exists on disk
            if os.path.exists(path):
                live_count += 1
                live_by_source[source] += 1
                if clean:
                    clean_records.append(rec)
            else:
                ghost_count += 1
                ghost_by_source[source] += 1
                if len(ghost_samples) < 20:
                    ghost_samples.append(path)

            if total % 100000 == 0:
                print(f"  checked {total} records...", file=sys.stderr)

    print(f"\n=== Ghost Audit Report ===")
    print(f"Index file:    {index_path}")
    print(f"Total records: {total}")
    print(f"Live records:  {live_count}")
    print(f"Ghost records: {ghost_count}")
    print(f"API records:   {api_count}")
    print(f"Ghost rate:    {ghost_count/total*100:.1f}%")

    print(f"\n--- Ghosts by source ---")
    for src, cnt in ghost_by_source.most_common():
        print(f"  {src}: {cnt}")

    print(f"\n--- Live by source ---")
    for src, cnt in live_by_source.most_common():
        print(f"  {src}: {cnt}")

    if ghost_samples:
        print(f"\n--- Sample ghost paths (first 20) ---")
        for p in ghost_samples:
            print(f"  {p}")

    if clean and output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            for rec in clean_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"\nClean index written: {output_path} ({len(clean_records)} records)")

    return ghost_count, live_count, total


def main():
    parser = argparse.ArgumentParser(description="Audit merged index for ghost entries")
    parser.add_argument("--index", type=Path, default=MERGED_INDEX, help="Index file to audit")
    parser.add_argument("--clean", action="store_true", help="Write ghost-free index")
    parser.add_argument("--output", type=Path, default=None, help="Output path for clean index")
    args = parser.parse_args()

    if args.clean and not args.output:
        args.output = args.index.parent / "index-clean.jsonl"

    audit(args.index, clean=args.clean, output_path=args.output)


if __name__ == "__main__":
    main()
