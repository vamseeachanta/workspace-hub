#!/usr/bin/env python3
"""Bridge extraction-report tables into the federated table index.

Deep extraction produces *-extraction-report.yaml files with CSV table paths,
but index_builder.py only reads *.manifest.yaml.  This script scans all
extraction reports, reads each referenced CSV to extract column headers and
row counts, then appends new entries to tables/index.jsonl (deduped by csv_path).

Usage:
    uv run --no-project python scripts/data/doc-intelligence/bridge-extraction-tables.py
    uv run --no-project python scripts/data/doc-intelligence/bridge-extraction-tables.py --dry-run
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_REPORTS_DIR = (
    _PROJECT_ROOT / "data" / "doc-intelligence" / "extraction-reports"
)
_DEFAULT_INDEX = (
    _PROJECT_ROOT / "data" / "doc-intelligence" / "tables" / "index.jsonl"
)


def _read_csv_meta(csv_path: Path) -> tuple[list[str], int]:
    """Return (columns, row_count) from a CSV file."""
    try:
        with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.reader(fh)
            header = next(reader, [])
            columns = [c.strip() for c in header]
            row_count = sum(1 for _ in reader)
        return columns, row_count
    except Exception:
        return [], 0


def _load_existing_paths(index_path: Path) -> set[str]:
    """Load csv_path values already in the index for dedup."""
    paths: set[str] = set()
    if not index_path.exists():
        return paths
    with open(index_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    paths.add(json.loads(line)["csv_path"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return paths


def bridge(
    reports_dir: Path,
    index_path: Path,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    """Scan extraction reports and append table entries to the index."""
    stats = {"reports_scanned": 0, "tables_found": 0, "tables_added": 0, "tables_skipped_missing": 0, "tables_deduped": 0}

    existing_paths = _load_existing_paths(index_path)
    new_records: list[dict] = []

    report_files = sorted(reports_dir.rglob("*-extraction-report.yaml"))
    if not report_files:
        print(f"No extraction reports found in {reports_dir}", file=sys.stderr)
        return stats

    for report_path in report_files:
        stats["reports_scanned"] += 1
        raw = yaml.safe_load(report_path.read_text())
        if not raw:
            continue

        document = raw.get("document", report_path.stem.replace("-extraction-report", ""))
        csv_paths = raw.get("tables", {}).get("csv_paths", [])

        # Determine domain from directory structure
        try:
            rel = report_path.relative_to(reports_dir)
            domain = rel.parts[0] if len(rel.parts) > 1 else "unknown"
        except ValueError:
            domain = "unknown"

        for abs_csv in csv_paths:
            stats["tables_found"] += 1
            abs_csv_path = Path(abs_csv)

            # Build a relative csv_path for the index (relative to data/doc-intelligence/)
            try:
                rel_csv = str(abs_csv_path.relative_to(_PROJECT_ROOT / "data" / "doc-intelligence"))
            except ValueError:
                # Fallback: use path from extraction-reports/ onward
                rel_csv = str(abs_csv_path.name)

            if rel_csv in existing_paths:
                stats["tables_deduped"] += 1
                continue

            if not abs_csv_path.exists():
                stats["tables_skipped_missing"] += 1
                if verbose:
                    print(f"  MISSING: {abs_csv_path}")
                continue

            columns, row_count = _read_csv_meta(abs_csv_path)

            record = {
                "title": None,
                "columns": columns,
                "row_count": row_count,
                "csv_path": rel_csv,
                "source": {
                    "document": document,
                },
                "domain": domain,
                "manifest": document,
            }
            new_records.append(record)
            existing_paths.add(rel_csv)
            stats["tables_added"] += 1

    if not dry_run and new_records:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "a") as fh:
            for rec in new_records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bridge extraction-report tables into the federated table index.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=_DEFAULT_REPORTS_DIR,
        help="Directory containing *-extraction-report.yaml files",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=_DEFAULT_INDEX,
        help="Path to tables/index.jsonl",
    )
    parser.add_argument("--dry-run", action="store_true", help="Scan only, don't write")
    parser.add_argument("--verbose", action="store_true", help="Print per-file details")

    args = parser.parse_args()

    if not args.reports_dir.exists():
        print(f"Error: reports directory not found: {args.reports_dir}", file=sys.stderr)
        return 1

    stats = bridge(args.reports_dir, args.index, dry_run=args.dry_run, verbose=args.verbose)

    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{mode}Bridge complete:")
    print(f"  Reports scanned:     {stats['reports_scanned']}")
    print(f"  Tables found:        {stats['tables_found']}")
    print(f"  Tables added:        {stats['tables_added']}")
    print(f"  Tables deduped:      {stats['tables_deduped']}")
    print(f"  Tables missing CSV:  {stats['tables_skipped_missing']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
