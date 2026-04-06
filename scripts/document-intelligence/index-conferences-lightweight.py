#!/usr/bin/env python3
"""Lightweight conference paper indexing script.

GitHub Issue: #1862

Scans known conference directories for PDF and TXT files, catalogs
metadata (filename, size, source, domain), appends new entries to
data/document-index/conference-index.jsonl, and writes a summary
manifest.json.  Resumable: already-indexed paths are skipped.
Never downloads anything.

Usage:
    uv run python scripts/document-intelligence/index-conferences-lightweight.py
    uv run python scripts/document-intelligence/index-conferences-lightweight.py --dry-run
    uv run python scripts/document-intelligence/index-conferences-lightweight.py --collection OMAE
    uv run python scripts/document-intelligence/index-conferences-lightweight.py --priority high
    uv run python scripts/document-intelligence/index-conferences-lightweight.py --stats-only
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
CONF_ROOT = Path("/mnt/ace/docs/conferences")

OUTPUT_JSONL = REPO_ROOT / "data" / "document-index" / "conference-index.jsonl"
OUTPUT_MANIFEST = REPO_ROOT / "data" / "document-index" / "conference-index-manifest.json"
CATALOG_PATH = REPO_ROOT / "data" / "document-index" / "conference-paper-catalog.yaml"

# Target extensions for this lightweight indexer (PDF + TXT only, per #1862)
TARGET_EXTS = {".pdf", ".txt"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_catalog() -> dict:
    """Load conference-paper-catalog.yaml if available.

    Returns a dict mapping collection name -> catalog entry (with domain info).
    Falls back to an empty dict if the catalog is missing or PyYAML is absent.
    """
    if not CATALOG_PATH.exists():
        print(f"  [warn] Catalog not found at {CATALOG_PATH} — domain info will be absent")
        return {}

    try:
        import yaml  # type: ignore
    except ImportError:
        print("  [warn] PyYAML not installed — domain info will be absent")
        return {}

    with open(CATALOG_PATH, "r") as f:
        data = yaml.safe_load(f)

    catalog: dict = {}
    for entry in data.get("conferences", []):
        name = entry.get("name", "")
        if name:
            catalog[name] = entry
    return catalog


def load_existing_paths(jsonl_path: Path) -> set:
    """Read existing JSONL and return a set of already-indexed absolute paths."""
    seen: set = set()
    if not jsonl_path.exists():
        return seen

    with open(jsonl_path, "r") as f:
        for line_no, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
                path = rec.get("path", "")
                if path:
                    seen.add(path)
            except json.JSONDecodeError:
                print(f"  [warn] Skipping malformed JSONL line {line_no}", file=sys.stderr)
    return seen


def extract_year(path: Path) -> Optional[str]:
    """Try to extract a 4-digit year (1980-2029) from path components."""
    for part in path.parts:
        m = re.search(r"\b(19[89]\d|20[012]\d)\b", part)
        if m:
            return m.group(1)
    return None


def infer_source(path: Path) -> str:
    """Return a short source tag based on path prefix."""
    try:
        rel = path.relative_to(CONF_ROOT)
        return "conferences/" + rel.parts[0] if rel.parts else "conferences"
    except ValueError:
        return str(path.parts[0]) if path.parts else "unknown"


# ---------------------------------------------------------------------------
# Core scan
# ---------------------------------------------------------------------------


def scan_collection(
    coll_path: Path,
    coll_name: str,
    catalog_entry: dict,
    seen_paths: set,
    dry_run: bool = False,
) -> list:
    """Scan a single collection directory for new PDF/TXT files.

    Returns a list of new record dicts (not yet written to disk).
    """
    new_records: list = []

    if not coll_path.is_dir():
        print(f"  [skip] {coll_name}: directory not found ({coll_path})")
        return new_records

    primary_domain = catalog_entry.get("primary_domain", "unknown")
    secondary_domains = catalog_entry.get("secondary_domains", [])

    skipped_existing = 0
    skipped_ext = 0

    for root, _dirs, files in os.walk(coll_path):
        for fname in sorted(files):
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()

            if ext not in TARGET_EXTS:
                skipped_ext += 1
                continue

            abs_path = str(fpath)

            if abs_path in seen_paths:
                skipped_existing += 1
                continue

            try:
                stat = fpath.stat()
            except OSError as exc:
                print(f"  [warn] Cannot stat {fpath}: {exc}", file=sys.stderr)
                continue

            year = extract_year(fpath)

            rec = {
                "collection": coll_name,
                "filename": fname,
                "path": abs_path,
                "extension": ext,
                "size_bytes": stat.st_size,
                "year": year,
                "source": infer_source(fpath),
                "domain": primary_domain,
                "secondary_domains": secondary_domains,
                "relative_path": str(fpath.relative_to(CONF_ROOT))
                if fpath.is_relative_to(CONF_ROOT)
                else str(fpath),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            }

            new_records.append(rec)
            # Update seen_paths in-place so duplicate paths within the same run
            # are also de-duplicated (edge case: symlinks / hard links).
            seen_paths.add(abs_path)

    status = "[dry-run]" if dry_run else "[scan]"
    print(
        f"  {status} {coll_name}: +{len(new_records)} new"
        f"  (skipped {skipped_existing} existing, {skipped_ext} non-target ext)"
    )

    return new_records


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------


def build_manifest(
    all_new: list,
    total_before: int,
    collections_scanned: list,
    collections_skipped: list,
    run_start: datetime,
    dry_run: bool,
) -> dict:
    """Build a manifest dict summarising the indexing run."""
    total_after = total_before + len(all_new)

    # Per-collection stats for new records
    coll_stats: dict = {}
    domain_stats: dict = {}

    for rec in all_new:
        coll = rec["collection"]
        domain = rec["domain"]
        ext = rec["extension"]

        if coll not in coll_stats:
            coll_stats[coll] = {"new_files": 0, "size_bytes": 0, "extensions": {}}
        coll_stats[coll]["new_files"] += 1
        coll_stats[coll]["size_bytes"] += rec["size_bytes"]
        coll_stats[coll]["extensions"][ext] = (
            coll_stats[coll]["extensions"].get(ext, 0) + 1
        )

        domain_stats[domain] = domain_stats.get(domain, 0) + 1

    # Convert size to MB for readability
    for cs in coll_stats.values():
        cs["size_mb"] = round(cs["size_bytes"] / (1024 * 1024), 2)

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "run_start": run_start.isoformat(),
        "dry_run": dry_run,
        "jsonl_path": str(OUTPUT_JSONL),
        "conf_root": str(CONF_ROOT),
        "totals": {
            "records_before": total_before,
            "new_records_this_run": len(all_new),
            "total_records_after": total_after,
        },
        "new_size_bytes": sum(r["size_bytes"] for r in all_new),
        "new_size_mb": round(sum(r["size_bytes"] for r in all_new) / (1024 * 1024), 2),
        "collections_scanned": sorted(collections_scanned),
        "collections_skipped": sorted(collections_skipped),
        "per_collection": coll_stats,
        "per_domain": domain_stats,
        "target_extensions": sorted(TARGET_EXTS),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    run_start = datetime.now(timezone.utc)

    parser = argparse.ArgumentParser(
        description="Lightweight conference paper indexer — catalog PDF/TXT files only."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report but do not write any files.",
    )
    parser.add_argument(
        "--collection",
        metavar="NAME",
        help="Limit scan to a single collection (partial case-insensitive match).",
    )
    parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        help="Only scan collections with this priority level (requires catalog).",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Print stats about the current JSONL index and exit.",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=OUTPUT_JSONL,
        help=f"Path to the JSONL index file (default: {OUTPUT_JSONL})",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        default=OUTPUT_MANIFEST,
        help=f"Path for the manifest.json output (default: {OUTPUT_MANIFEST})",
    )
    args = parser.parse_args()

    jsonl_path: Path = args.output_jsonl
    manifest_path: Path = args.output_manifest

    # ------------------------------------------------------------------
    # Stats-only mode
    # ------------------------------------------------------------------
    if args.stats_only:
        print(f"Loading existing index: {jsonl_path}")
        seen = load_existing_paths(jsonl_path)
        print(f"  Total records: {len(seen)}")
        if manifest_path.exists():
            with open(manifest_path) as f:
                mf = json.load(f)
            print(f"  Last manifest: {mf.get('generated', 'unknown')}")
            totals = mf.get("totals", {})
            print(f"  Records before last run: {totals.get('records_before', '?')}")
            print(f"  New in last run: {totals.get('new_records_this_run', '?')}")
            dom = mf.get("per_domain", {})
            if dom:
                print("  Domain breakdown (last run new records):")
                for d, n in sorted(dom.items(), key=lambda x: -x[1]):
                    print(f"    {d:30s} {n:>6,d}")
        return 0

    # ------------------------------------------------------------------
    # Load catalog and existing index
    # ------------------------------------------------------------------
    print(f"Loading catalog from {CATALOG_PATH}")
    catalog = load_catalog()
    print(f"  {len(catalog)} collections in catalog")

    print(f"\nLoading existing index: {jsonl_path}")
    seen_paths = load_existing_paths(jsonl_path)
    total_before = len(seen_paths)
    print(f"  {total_before:,} paths already indexed — these will be skipped")

    # ------------------------------------------------------------------
    # Determine which collections to scan
    # ------------------------------------------------------------------
    if not CONF_ROOT.is_dir():
        print(f"\nERROR: Conference root not found: {CONF_ROOT}", file=sys.stderr)
        print("This script does not download anything; mount the volume and retry.")
        return 1

    raw_collections = sorted(d.name for d in CONF_ROOT.iterdir() if d.is_dir())
    print(f"\nFound {len(raw_collections)} conference directories under {CONF_ROOT}")

    collections_to_scan: list = []
    collections_skipped_by_filter: list = []

    for cname in raw_collections:
        # Collection name filter
        if args.collection and args.collection.lower() not in cname.lower():
            collections_skipped_by_filter.append(cname)
            continue

        # Priority filter (requires catalog entry)
        if args.priority:
            entry = catalog.get(cname, {})
            coll_priority = entry.get("priority", "medium")
            if coll_priority != args.priority:
                collections_skipped_by_filter.append(cname)
                continue

        collections_to_scan.append(cname)

    if collections_skipped_by_filter:
        print(
            f"  Filtered out {len(collections_skipped_by_filter)} collections"
            f" (--collection / --priority flags)."
        )

    print(f"  Scanning {len(collections_to_scan)} collections\n")

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------
    all_new: list = []
    scanned_names: list = []

    for cname in collections_to_scan:
        coll_path = CONF_ROOT / cname
        catalog_entry = catalog.get(cname, {})
        new_recs = scan_collection(
            coll_path=coll_path,
            coll_name=cname,
            catalog_entry=catalog_entry,
            seen_paths=seen_paths,  # mutated in-place
            dry_run=args.dry_run,
        )
        all_new.extend(new_recs)
        scanned_names.append(cname)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total_size_mb = sum(r["size_bytes"] for r in all_new) / (1024 * 1024)
    print(f"\n{'=' * 60}")
    print(f"  New records this run : {len(all_new):>8,d}")
    print(f"  Total size (new)     : {total_size_mb:>8.1f} MB")
    print(f"  Total after indexing : {total_before + len(all_new):>8,d}")
    print(f"{'=' * 60}")

    if args.dry_run:
        print("\n[DRY RUN] No files written.")
        manifest = build_manifest(
            all_new, total_before, scanned_names, collections_skipped_by_filter,
            run_start, dry_run=True,
        )
        print(json.dumps(manifest, indent=2))
        return 0

    if not all_new:
        print("\nNo new records — index is up to date.")
        # Still refresh the manifest so the timestamp is current
        manifest = build_manifest(
            [], total_before, scanned_names, collections_skipped_by_filter,
            run_start, dry_run=False,
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest updated: {manifest_path}")
        return 0

    # ------------------------------------------------------------------
    # Append new records to JSONL
    # ------------------------------------------------------------------
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "a") as f:
        for rec in all_new:
            f.write(json.dumps(rec) + "\n")
    print(f"\nAppended {len(all_new):,} records to {jsonl_path}")

    # ------------------------------------------------------------------
    # Write manifest.json
    # ------------------------------------------------------------------
    manifest = build_manifest(
        all_new, total_before, scanned_names, collections_skipped_by_filter,
        run_start, dry_run=False,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written:  {manifest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
