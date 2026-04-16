"""Shared metadata-carryover helper for Phase A/C/E rewrites of index.jsonl (#1878).

Every pipeline stage that rewrites the full index.jsonl must preserve the
enriched fields (`content_type`, `summary_done`) populated by
`enrich-summary-metadata.py`. Without carryover, each rewrite regresses the
index back to the #1878 broken state.

Usage in a pipeline stage:

    from _carryover_metadata import (
        extract_enriched_fields, apply_carryover, atomic_write_index,
    )

    side = extract_enriched_fields(index_path)  # {path -> {content_type, summary_done}}
    new_records = build_new_records(...)         # stage-specific logic
    merged = apply_carryover(new_records, side)
    atomic_write_index(index_path, merged)
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
from pathlib import Path
from typing import Iterable

CARRYOVER_FIELDS: tuple[str, ...] = ("content_type", "summary_done")


def extract_enriched_fields(index_path: Path) -> dict[str, dict]:
    """Return {path -> {content_type, summary_done}} for records that have them."""
    index_path = Path(index_path)
    if not index_path.exists():
        return {}
    out: dict[str, dict] = {}
    with open(index_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            path = rec.get("path")
            if not path:
                continue
            fields = {k: rec[k] for k in CARRYOVER_FIELDS if k in rec}
            if fields:
                out[path] = fields
    return out


def apply_carryover(records: Iterable[dict], side: dict[str, dict]) -> list[dict]:
    """Merge side-dict fields into records keyed by path, without overwriting
    any value the record already sets (newer values win)."""
    out: list[dict] = []
    for r in records:
        path = r.get("path")
        if path and path in side:
            for k, v in side[path].items():
                r.setdefault(k, v)
        out.append(r)
    return out


def atomic_write_index(
    index_path: Path,
    records: Iterable[dict],
    *,
    today: str | None = None,
) -> None:
    """Write records to index_path atomically. Create a dated backup of the
    existing file first (idempotent — does not overwrite an existing backup)."""
    index_path = Path(index_path)
    today = today or _dt.date.today().isoformat()
    backup_path = index_path.with_name(f"{index_path.name}.backup-{today}")

    if index_path.exists() and not backup_path.exists():
        shutil.copy2(index_path, backup_path)

    tmp_path = index_path.with_suffix(index_path.suffix + ".tmp")
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp_path, index_path)
