#!/usr/bin/env python3
"""Build federated content indexes from document extraction manifests.

Reads *.manifest.yaml files produced by extract-document.py and generates
8 content-type JSONL indexes for fast querying without re-parsing sources.

Usage:
    uv run --no-project python scripts/data/doc-intelligence/build-doc-intelligence.py
    uv run --no-project python scripts/data/doc-intelligence/build-doc-intelligence.py --force
    uv run --no-project python scripts/data/doc-intelligence/build-doc-intelligence.py --dry-run
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
_project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))

from scripts.data.doc_intelligence.index_builder import build_indexes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build federated content indexes from document manifests.",
    )
    parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=_project_root / "data" / "doc-intelligence" / "manifests",
        help="Directory containing *.manifest.yaml files (default: data/doc-intelligence/manifests)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_project_root / "data" / "doc-intelligence",
        help="Where to write JSONL indexes (default: data/doc-intelligence)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild all manifests, ignoring checksums",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-manifest details",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan only, don't write any files",
    )

    args = parser.parse_args()

    if not args.manifest_dir.exists():
        print(f"Error: manifest directory not found: {args.manifest_dir}", file=sys.stderr)
        return 1

    stats = build_indexes(
        manifest_dir=args.manifest_dir,
        output_dir=args.output_dir,
        force=args.force,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{mode}Build complete:")
    print(f"  Manifests processed: {stats.manifests_processed}")
    print(f"  Manifests skipped:   {stats.manifests_skipped}")
    print(f"  Tables written:      {stats.tables_written}")
    print(f"  Curves indexed:      {stats.curves_written}")
    if stats.records_by_type:
        print("  Records by type:")
        for ct, count in sorted(stats.records_by_type.items()):
            if count > 0:
                print(f"    {ct}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
