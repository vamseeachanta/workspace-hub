#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""Enrich data/document-index/index.jsonl with content_type and summary_done.

content_type: derived from `ext` via content_type_map.yaml (fallback: "other").
summary_done: True iff a matching summary file exists on disk AND has non-empty
              `summary` text. See _summary_lookup.py for the four filename
              conventions that coexist on the ace drive.

Usage:
    # Dry run — coverage report only, no writes
    uv run --no-project python scripts/data/document-index/enrich-summary-metadata.py --dry-run

    # Full enrichment, 8 parallel workers, resume-safe
    uv run --no-project python scripts/data/document-index/enrich-summary-metadata.py --workers 8 --resume
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

import yaml

from _summary_lookup import find_summary

_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_MAP_PATH = _THIS_DIR / "content_type_map.yaml"
DEFAULT_SUMMARIES_DIR = Path("/mnt/ace/data/document-index/summaries")


@lru_cache(maxsize=1)
def _load_map(path: str = str(DEFAULT_MAP_PATH)) -> dict[str, str]:
    """Flatten content_type_map.yaml into {ext_lower: content_type}."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    flat: dict[str, str] = {}
    for content_type, exts in raw.items():
        for ext in exts or []:
            flat[str(ext).lower()] = str(content_type)
    return flat


def content_type_for_ext(ext: str | None) -> str:
    """Map a file extension to a content_type. Unknown → 'other' (never None)."""
    if not ext:
        return "other"
    key = ext.lower().lstrip(".")
    return _load_map().get(key, "other")


def summary_done_from_file(path: Path) -> bool:
    """True iff file exists, parses as JSON, and has non-empty `summary` text."""
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError, OSError):
        return False
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return False
    summary = data.get("summary")
    if not isinstance(summary, str):
        return False
    return bool(summary.strip())


def enrich_one(record: dict, summaries_dir: Path) -> dict:
    """Add content_type, summary_file_exists, summary_done — preserves all other fields.

    #2309: the two summary signals are decoupled.
      - summary_file_exists: True iff find_summary() resolved to a file on disk
      - summary_done:        True iff the file exists AND its `summary` text is non-empty
    """
    record["content_type"] = content_type_for_ext(record.get("ext"))
    summary_path = find_summary(record, summaries_dir)
    record["summary_file_exists"] = summary_path is not None
    record["summary_done"] = (
        False if summary_path is None else summary_done_from_file(summary_path)
    )
    return record


def _enrich_worker(payload: tuple[str, str]) -> str:
    """Worker used by ProcessPoolExecutor. Takes (record_json, summaries_dir_str)."""
    record_json, summaries_dir_str = payload
    record = json.loads(record_json)
    enriched = enrich_one(record, Path(summaries_dir_str))
    return json.dumps(enriched, ensure_ascii=False)


def _is_already_enriched(record: dict) -> bool:
    # #2309: must include summary_file_exists — otherwise --resume skips pre-split records
    return (
        "content_type" in record
        and "summary_done" in record
        and "summary_file_exists" in record
    )


def enrich_index(
    *,
    index_path: Path,
    summaries_dir: Path,
    workers: int = 1,
    resume: bool = False,
    dry_run: bool = False,
    today: str | None = None,
) -> dict:
    """Enrich an index.jsonl in place with atomic write + dated backup.

    Returns a stats dict for dry-run reporting / logging."""
    today = today or _dt.date.today().isoformat()
    index_path = Path(index_path)
    summaries_dir = Path(summaries_dir)

    records: list[dict] = []
    with open(index_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    stats = {
        "total": len(records),
        "content_type_non_other": 0,
        "summary_done_true": 0,
        "summary_file_exists_true": 0,  # #2309
    }
    out_records: list[dict] = []

    if workers <= 1:
        for r in records:
            if resume and _is_already_enriched(r):
                out_records.append(r)
                continue
            out_records.append(enrich_one(r, summaries_dir))
    else:
        indices_to_enrich: list[int] = []
        out_records = [None] * len(records)  # type: ignore[list-item]
        for i, r in enumerate(records):
            if resume and _is_already_enriched(r):
                out_records[i] = r
            else:
                indices_to_enrich.append(i)

        payloads = [
            (json.dumps(records[i], ensure_ascii=False), str(summaries_dir))
            for i in indices_to_enrich
        ]
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futures = {
                ex.submit(_enrich_worker, p): i for i, p in zip(indices_to_enrich, payloads)
            }
            for fut in as_completed(futures):
                i = futures[fut]
                out_records[i] = json.loads(fut.result())

    for r in out_records:
        if r.get("content_type") and r.get("content_type") != "other":
            stats["content_type_non_other"] += 1
        if r.get("summary_done") is True:
            stats["summary_done_true"] += 1
        if r.get("summary_file_exists") is True:
            stats["summary_file_exists_true"] += 1

    if dry_run:
        return stats

    backup_path = index_path.with_name(f"{index_path.name}.backup-{today}")
    if not backup_path.exists():
        shutil.copy2(index_path, backup_path)

    tmp_path = index_path.with_suffix(index_path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for r in out_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp_path, index_path)
    return stats


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--index", type=Path, default=Path("data/document-index/index.jsonl"))
    p.add_argument("--summaries-dir", type=Path, default=DEFAULT_SUMMARIES_DIR)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--resume", action="store_true", help="Skip records that already have both fields")
    p.add_argument("--dry-run", action="store_true", help="Report coverage without writing")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    stats = enrich_index(
        index_path=args.index,
        summaries_dir=args.summaries_dir,
        workers=args.workers,
        resume=args.resume,
        dry_run=args.dry_run,
    )
    total = stats["total"] or 1
    pct_ct = 100.0 * stats["content_type_non_other"] / total
    pct_sd = 100.0 * stats["summary_done_true"] / total
    print(
        f"Enriched {stats['total']} records. "
        f"content_type non-other: {stats['content_type_non_other']} ({pct_ct:.1f}%). "
        f"summary_done true: {stats['summary_done_true']} ({pct_sd:.1f}%)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
