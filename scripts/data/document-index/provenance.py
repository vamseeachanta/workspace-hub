#!/usr/bin/env python3
# ABOUTME: Multi-source provenance tracking layer for the document index pipeline.
# ABOUTME: Merges duplicate records (by content_hash) into a single entry with a provenance array.

"""
Provenance Tracking Layer
=========================

When the same document appears in multiple sources (e.g. og_standards and
ace_project), the current pipeline creates separate index.jsonl entries.
This module merges those duplicates into a single canonical record with a
``provenance`` array that tracks every location where the document was found.

Dedup key: ``content_hash`` (SHA-256 of file content).

Usage — standalone migration of an existing index.jsonl::

    python provenance.py data/document-index/index.jsonl --output data/document-index/index-merged.jsonl

Usage — as a library from the indexing pipeline::

    from scripts.data.document_index.provenance import merge_provenance

    merged = merge_provenance(records, source_priority=["og_standards", "ace_standards", ...])
"""

import argparse
import json
import logging
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Default source priority — lower index = higher priority.  Matches config.yaml.
DEFAULT_SOURCE_PRIORITY: List[str] = [
    "og_standards",
    "ace_standards",
    "ace_project",
    "dde_project",
    "workspace_spec",
    "api_metadata",
]

# Fields that should NOT be overwritten by a lower-priority source.
# The primary record's values for these are authoritative.
_AUTHORITATIVE_FIELDS = frozenset({
    "content_hash",
    "ext",
    "size_mb",
    "is_cad",
})


def _make_provenance_entry(
    record: Dict[str, Any],
    discovered: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a single provenance entry from an index record.

    Schema::

        {
            "source": "og_standards",
            "path": "/mnt/ace/O&G-Standards/...",
            "host": "ace-linux-1",
            "discovered": "2026-03-25T00:00:00+00:00"
        }
    """
    entry: Dict[str, Any] = {
        "source": record.get("source", "unknown"),
        "path": record.get("path", ""),
        "host": record.get("host", "unknown"),
        "discovered": discovered or _now_iso(),
    }
    # Preserve og_db_id when the source is og_standards
    if record.get("og_db_id") is not None:
        entry["og_db_id"] = record["og_db_id"]
    # Preserve old_path if the record was remapped
    if record.get("old_path"):
        entry["old_path"] = record["old_path"]
    return entry


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _source_rank(source: str, priority: Sequence[str]) -> int:
    """Return the priority rank (lower = more authoritative)."""
    try:
        return priority.index(source)
    except ValueError:
        return len(priority)


def _pick_primary(
    records: List[Dict[str, Any]],
    priority: Sequence[str],
) -> Dict[str, Any]:
    """Among records sharing the same content_hash, pick the primary.

    The primary is the record from the highest-priority source.  Ties within
    the same source are broken by earliest mtime.
    """
    def sort_key(rec: Dict[str, Any]):
        rank = _source_rank(rec.get("source", ""), priority)
        mtime = rec.get("mtime", "") or ""
        return (rank, mtime)

    return min(records, key=sort_key)


def _merge_enrichments(
    primary: Dict[str, Any],
    secondary: Dict[str, Any],
) -> None:
    """Copy non-None enrichment fields from secondary into primary if primary
    has them as None or missing.  Authoritative fields are never overwritten.
    """
    for key, value in secondary.items():
        if key in _AUTHORITATIVE_FIELDS:
            continue
        if key in ("path", "host", "source", "provenance", "duplicate_of"):
            continue
        if value is None:
            continue
        existing = primary.get(key)
        if existing is None:
            primary[key] = value
        # Merge list fields like target_repos
        elif isinstance(existing, list) and isinstance(value, list):
            merged = list(existing)
            for item in value:
                if item not in merged:
                    merged.append(item)
            primary[key] = merged


def merge_provenance(
    records: List[Dict[str, Any]],
    source_priority: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Merge index records that share a content_hash into single entries with
    a provenance array.

    Args:
        records: Flat list of index.jsonl record dicts.
        source_priority: Ordered list of source names (highest priority first).
            Defaults to :data:`DEFAULT_SOURCE_PRIORITY`.

    Returns:
        List of merged records.  Records without a content_hash are passed
        through unchanged (with a single-element provenance array).
    """
    priority = source_priority or DEFAULT_SOURCE_PRIORITY

    # Group records by content_hash
    hash_groups: Dict[str, List[Dict[str, Any]]] = {}
    no_hash: List[Dict[str, Any]] = []

    for rec in records:
        h = rec.get("content_hash")
        if not h:
            no_hash.append(rec)
            continue
        hash_groups.setdefault(h, []).append(rec)

    merged: List[Dict[str, Any]] = []
    merge_count = 0

    for content_hash, group in hash_groups.items():
        primary = deepcopy(_pick_primary(group, priority))

        # Build provenance array from all records in the group
        provenance_entries: List[Dict[str, Any]] = []
        seen_paths = set()
        for rec in group:
            p = rec.get("path", "")
            if p in seen_paths:
                continue
            seen_paths.add(p)
            provenance_entries.append(_make_provenance_entry(rec))
            # Merge any enrichment data the secondary might have
            if rec is not group[0] or rec.get("path") != primary.get("path"):
                _merge_enrichments(primary, rec)

        # Sort provenance: primary source first, then alphabetical
        provenance_entries.sort(
            key=lambda e: (
                _source_rank(e["source"], priority),
                e.get("path", ""),
            )
        )

        primary["provenance"] = provenance_entries

        # Remove the legacy duplicate_of field — provenance replaces it
        primary.pop("duplicate_of", None)

        if len(group) > 1:
            merge_count += 1

        merged.append(primary)

    # Handle records without content_hash (CAD files, API metadata, etc.)
    for rec in no_hash:
        rec_copy = deepcopy(rec)
        rec_copy["provenance"] = [_make_provenance_entry(rec)]
        rec_copy.pop("duplicate_of", None)
        merged.append(rec_copy)

    logger.info(
        "Provenance merge: %d input records -> %d merged records "
        "(%d content-hash groups had duplicates)",
        len(records), len(merged), merge_count,
    )
    return merged


# ---------------------------------------------------------------------------
# Streaming version for large files (avoids loading all 1M records at once)
# ---------------------------------------------------------------------------

def merge_provenance_streaming(
    input_path: Path,
    output_path: Path,
    source_priority: Optional[List[str]] = None,
    chunk_log_interval: int = 100_000,
) -> Dict[str, int]:
    """Stream-merge an index.jsonl file, grouping by content_hash.

    This version does two passes:
      1. Build hash->records map (memory: stores full records keyed by hash).
      2. Write merged output.

    For a 1M-record file this needs ~2-4 GB RAM — acceptable for a batch job.

    Returns:
        Stats dict with input_count, output_count, merged_groups, no_hash_count.
    """
    priority = source_priority or DEFAULT_SOURCE_PRIORITY

    hash_groups: Dict[str, List[Dict[str, Any]]] = {}
    no_hash: List[Dict[str, Any]] = []
    input_count = 0

    logger.info("Pass 1: reading %s", input_path)
    with open(input_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            input_count += 1
            if input_count % chunk_log_interval == 0:
                logger.info("  read %d records...", input_count)

            h = rec.get("content_hash")
            if not h:
                no_hash.append(rec)
            else:
                hash_groups.setdefault(h, []).append(rec)

    logger.info(
        "Pass 1 done: %d records, %d unique hashes, %d without hash",
        input_count, len(hash_groups), len(no_hash),
    )

    # Pass 2: merge and write
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".jsonl.tmp")
    output_count = 0
    merged_groups = 0

    logger.info("Pass 2: writing merged output to %s", output_path)
    with open(tmp_path, "w") as fh:
        for content_hash, group in hash_groups.items():
            primary = _pick_primary(group, priority)
            # Build a fresh primary (deep copy to avoid mutating input)
            out = deepcopy(primary)

            provenance_entries = []
            seen_paths = set()
            for rec in group:
                p = rec.get("path", "")
                if p in seen_paths:
                    continue
                seen_paths.add(p)
                provenance_entries.append(_make_provenance_entry(rec))
                if rec.get("path") != out.get("path"):
                    _merge_enrichments(out, rec)

            provenance_entries.sort(
                key=lambda e: (
                    _source_rank(e["source"], priority),
                    e.get("path", ""),
                )
            )

            out["provenance"] = provenance_entries
            out.pop("duplicate_of", None)

            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
            output_count += 1
            if len(group) > 1:
                merged_groups += 1

        for rec in no_hash:
            out = deepcopy(rec)
            out["provenance"] = [_make_provenance_entry(rec)]
            out.pop("duplicate_of", None)
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
            output_count += 1

    # Atomic rename
    import os
    os.replace(tmp_path, output_path)

    stats = {
        "input_count": input_count,
        "output_count": output_count,
        "merged_groups": merged_groups,
        "no_hash_count": len(no_hash),
    }
    logger.info(
        "Pass 2 done: %d -> %d records (%d groups merged)",
        input_count, output_count, merged_groups,
    )
    return stats


# ---------------------------------------------------------------------------
# Integration hook for phase-a-index.py
# ---------------------------------------------------------------------------

def apply_provenance_to_pipeline(
    existing: Dict[str, Dict[str, Any]],
    new_records: List[Dict[str, Any]],
    source_priority: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Integration point for the indexing pipeline.

    Called after scanning all sources but before writing index.jsonl.
    Instead of keying by path (which creates duplicates), this groups by
    content_hash and merges records.

    Args:
        existing: Current index keyed by path (from load_existing_index).
        new_records: Newly scanned records from all sources.
        source_priority: Source priority order.

    Returns:
        Merged index keyed by content_hash (or path for hash-less records).
    """
    priority = source_priority or DEFAULT_SOURCE_PRIORITY

    # Combine all records
    all_records = list(existing.values()) + new_records

    # Merge
    merged_list = merge_provenance(all_records, source_priority=priority)

    # Re-key: use content_hash as primary key where available, else path
    merged_index: Dict[str, Dict[str, Any]] = {}
    for rec in merged_list:
        key = rec.get("content_hash") or rec.get("path", "")
        merged_index[key] = rec

    return merged_index


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge duplicate index.jsonl entries into records with provenance arrays"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to input index.jsonl",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output path (default: overwrite input)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print stats without writing",
    )
    parser.add_argument(
        "--priority",
        nargs="+",
        default=None,
        help="Source priority list (space-separated, highest first)",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_path = (args.output or args.input).resolve()

    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return 1

    if args.dry_run:
        # Quick stats pass
        hash_counts: Dict[str, int] = {}
        no_hash = 0
        total = 0
        with open(input_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                h = rec.get("content_hash")
                if h:
                    hash_counts[h] = hash_counts.get(h, 0) + 1
                else:
                    no_hash += 1

        dupes = sum(1 for c in hash_counts.values() if c > 1)
        dupe_records = sum(c for c in hash_counts.values() if c > 1)
        unique = sum(1 for c in hash_counts.values() if c == 1)
        print(f"Total records:          {total}")
        print(f"Unique content hashes:  {len(hash_counts)}")
        print(f"No content hash:        {no_hash}")
        print(f"Hash groups with dupes: {dupes}")
        print(f"Records in dupe groups: {dupe_records}")
        print(f"After merge would be:   {len(hash_counts) + no_hash}")
        print(f"Records saved:          {total - len(hash_counts) - no_hash}")
        return 0

    stats = merge_provenance_streaming(
        input_path,
        output_path,
        source_priority=args.priority,
    )
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
