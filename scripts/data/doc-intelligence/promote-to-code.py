#!/usr/bin/env python3
"""Promote doc-intelligence JSONL indexes into executable code artifacts.

Reads content-type indexes produced by build-doc-intelligence.py and generates
Python modules, YAML skills, CSV files, and test scaffolds.

Usage:
    uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py
    uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py --dry-run
    uv run --no-project python scripts/data/doc-intelligence/promote-to-code.py --types tables --verbose
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
_project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))

from scripts.data.doc_intelligence.promoters.coordinator import promote_all


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote doc-intelligence indexes into code artifacts.",
    )
    parser.add_argument(
        "--index-dir",
        type=Path,
        default=_project_root / "data" / "doc-intelligence",
        help="Directory containing JSONL indexes (default: data/doc-intelligence)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=_project_root,
        help="Workspace root for output path resolution",
    )
    parser.add_argument(
        "--types",
        nargs="+",
        help="Only promote these content types (e.g. --types tables constants)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-type details",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be written without writing",
    )

    args = parser.parse_args()

    if not args.index_dir.exists():
        print(f"Error: index directory not found: {args.index_dir}", file=sys.stderr)
        return 1

    stats = promote_all(
        index_dir=args.index_dir,
        project_root=args.project_root,
        dry_run=args.dry_run,
        verbose=args.verbose,
        types=args.types,
    )

    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{mode}Promotion complete:")
    print(f"  Files written:  {stats.total_written}")
    print(f"  Files skipped:  {stats.total_skipped}")
    print(f"  Errors:         {stats.total_errors}")

    if stats.results_by_type:
        print("  By type:")
        for ct, result in sorted(stats.results_by_type.items()):
            w = len(result.files_written)
            s = len(result.files_skipped)
            e = len(result.errors)
            print(f"    {ct}: {w} written, {s} skipped, {e} errors")

    return 1 if stats.total_errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
