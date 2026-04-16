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

(The CLI wiring + parallel/resume machinery lands in Wave 3. Wave 2 ships the
pure-function core: content_type_for_ext, summary_done_from_file, enrich_one.)
"""

from __future__ import annotations

import json
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
    """Add content_type + summary_done to a record, preserving all other fields."""
    record["content_type"] = content_type_for_ext(record.get("ext"))
    summary_path = find_summary(record, summaries_dir)
    record["summary_done"] = (
        False if summary_path is None else summary_done_from_file(summary_path)
    )
    return record
