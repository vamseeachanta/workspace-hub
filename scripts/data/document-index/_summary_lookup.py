"""Multi-pattern summary filename resolver for index.jsonl enrichment (#1878).

Four filename conventions coexist in /mnt/ace/data/document-index/summaries/:
    601,320 × <16hex>.json            — path-derived (sha256(path)[:16])
     78,274 × sha256:<64hex>.json     — full prefixed content_hash
     27,083 × <32hex>.json            — bare md5 (legacy og_standards)
     10,460 × <64hex>.json            — bare sha256 (legacy / prefix-stripped)

Lookup order: prefixed → bare → path-fallback.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def candidate_filenames(record: dict) -> list[str]:
    """Ordered candidate summary filenames for a record."""
    ch = record.get("content_hash") or None
    path = record["path"]
    path_key = hashlib.sha256(path.encode()).hexdigest()[:16]

    candidates: list[str] = []
    if ch:
        candidates.append(f"{ch}.json")
        if ":" in ch:
            _, bare = ch.split(":", 1)
            candidates.append(f"{bare}.json")
    candidates.append(f"{path_key}.json")
    return candidates


def find_summary(record: dict, summaries_dir: Path) -> Path | None:
    """Return the first existing candidate path, or None."""
    for name in candidate_filenames(record):
        p = summaries_dir / name
        if p.exists():
            return p
    return None
