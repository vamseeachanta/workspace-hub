#!/usr/bin/env python3
"""
Conference Indexing Preparation Script
GitHub Issue: #1612

Reads conference-paper-catalog.yaml and generates a batch JSONL file
for Phase A indexing. Walks conference directories to build a complete
file list of indexable documents (.pdf, .doc, .docx).

Usage:
    python prep-conference-index.py --priority-only
    python prep-conference-index.py --output custom-output.jsonl
    python prep-conference-index.py  # all conferences
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# Extensions to include for indexing
INDEXABLE_EXTENSIONS = {'.pdf', '.doc', '.docx'}

# Default paths relative to workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]  # scripts/data/document-index -> workspace root
DEFAULT_CATALOG = WORKSPACE_ROOT / "data" / "document-index" / "conference-paper-catalog.yaml"
DEFAULT_OUTPUT = WORKSPACE_ROOT / "data" / "document-index" / "conference-index-batch.jsonl"


def load_catalog(catalog_path: Path) -> dict:
    """Load the conference paper catalog YAML."""
    if not catalog_path.exists():
        print(f"ERROR: Catalog not found: {catalog_path}", file=sys.stderr)
        sys.exit(1)

    with open(catalog_path, 'r') as f:
        return yaml.safe_load(f)


def walk_conference_dir(conf_path: str) -> list:
    """
    Walk a conference directory and return all indexable files.
    Returns list of (relative_path, extension) tuples.
    """
    results = []
    conf_dir = Path(conf_path)

    if not conf_dir.exists():
        return results

    for root, dirs, files in os.walk(conf_dir):
        for fname in sorted(files):
            ext = Path(fname).suffix.lower()
            if ext in INDEXABLE_EXTENSIONS:
                full_path = os.path.join(root, fname)
                results.append((full_path, ext))

    return results


def generate_batch(catalog: dict, priority_only: bool = False) -> tuple:
    """
    Generate batch entries for conference indexing.

    Returns:
        (entries, summary) where entries is list of dicts and
        summary is dict of conference -> file count
    """
    conferences = catalog.get('conferences', [])
    entries = []
    summary = {}
    skipped = []

    for conf in conferences:
        name = conf.get('name', 'Unknown')
        path = conf.get('path', '')
        priority = conf.get('priority', 'medium')

        if priority_only and priority != 'high':
            skipped.append(f"  SKIP  {name} (priority: {priority})")
            continue

        files = walk_conference_dir(path)

        if not files:
            skipped.append(f"  SKIP  {name} (no indexable files found at {path})")
            continue

        conf_count = 0
        for file_path, ext in files:
            entry = {
                "source": "conferences",
                "conference": name,
                "path": file_path,
                "extension": ext
            }
            entries.append(entry)
            conf_count += 1

        if conf_count > 0:
            summary[name] = conf_count

    return entries, summary, skipped


def write_batch(entries: list, output_path: Path):
    """Write batch entries as JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description="Prepare conference paper indexing batch from catalog YAML."
    )
    parser.add_argument(
        '--catalog',
        type=Path,
        default=DEFAULT_CATALOG,
        help=f"Path to conference-paper-catalog.yaml (default: {DEFAULT_CATALOG})"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSONL batch file path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        '--priority-only',
        action='store_true',
        default=False,
        help="Only include conferences with priority: high"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help="Print summary without writing output file"
    )

    args = parser.parse_args()

    # Load catalog
    print(f"Loading catalog: {args.catalog}")
    catalog = load_catalog(args.catalog)

    total_conferences = catalog.get('total_conferences', '?')
    print(f"Catalog contains {total_conferences} conferences")
    print()

    # Generate batch
    mode = "priority-only (high)" if args.priority_only else "all conferences"
    print(f"Mode: {mode}")
    print("-" * 60)

    entries, summary, skipped = generate_batch(catalog, priority_only=args.priority_only)

    # Print skip log
    if skipped:
        for msg in skipped:
            print(msg)
        print()

    # Print summary
    print("=" * 60)
    print("CONFERENCE INDEXING SUMMARY")
    print("=" * 60)

    grand_total = 0
    for conf_name, count in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {conf_name:50s} {count:>6,d} files")
        grand_total += count

    print("-" * 60)
    print(f"  {'TOTAL':50s} {grand_total:>6,d} files")
    print(f"  Conferences included: {len(summary)}")
    if args.priority_only:
        print(f"  (filtered to priority: high only)")
    print("=" * 60)

    # Write output
    if not args.dry_run:
        write_batch(entries, args.output)
        print(f"\nBatch written to: {args.output}")
        print(f"  Lines: {len(entries)}")
        file_size = args.output.stat().st_size
        if file_size > 1024 * 1024:
            print(f"  Size: {file_size / (1024*1024):.1f} MB")
        else:
            print(f"  Size: {file_size / 1024:.1f} KB")
    else:
        print("\n[DRY RUN - no output written]")

    return 0


if __name__ == '__main__':
    sys.exit(main())
