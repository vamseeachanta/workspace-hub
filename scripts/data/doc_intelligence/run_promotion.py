#!/usr/bin/env python3
# ABOUTME: CLI wrapper for promotion coordinator — runs promoters on JSONL indexes
# ABOUTME: Usage: python scripts/data/doc_intelligence/run_promotion.py [--types worked_examples]

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.data.doc_intelligence.promoters.coordinator import promote_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Run doc-intelligence promoters")
    parser.add_argument(
        "--index-dir", type=Path,
        default=Path(__file__).resolve().parents[3] / "data/doc-intelligence",
    )
    parser.add_argument(
        "--project-root", type=Path,
        default=Path(__file__).resolve().parents[3],
    )
    parser.add_argument("--types", nargs="*", help="Content types to promote")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true", default=True)
    args = parser.parse_args()

    stats = promote_all(
        index_dir=args.index_dir,
        project_root=args.project_root,
        dry_run=args.dry_run,
        verbose=args.verbose,
        types=args.types,
    )
    print(f"\n=== TOTAL: {stats.total_written} written, "
          f"{stats.total_skipped} skipped, {stats.total_errors} errors ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
