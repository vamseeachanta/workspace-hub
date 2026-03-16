#!/usr/bin/env python3
# ABOUTME: Remap og_standards index paths from old directory to inventory DB target_path (WRK-1254)
# ABOUTME: Joins on og_db_id to fix 27,504 stale paths pointing to removed /mnt/ace/0000 O&G/

"""
Remap og_standards entries in index.jsonl using the inventory DB's target_path column.

The og_standards source was indexed from /mnt/ace/0000 O&G/0000 Codes & Standards/
which no longer exists. The inventory DB at /mnt/ace/O&G-Standards/_inventory.db
has a target_path column mapping each file to its new location.

Usage:
    uv run --no-project python scripts/data/document-index/remap-og-standards-paths.py
    uv run --no-project python scripts/data/document-index/remap-og-standards-paths.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_DB = "/mnt/ace/O&G-Standards/_inventory.db"
DEFAULT_INDEX = HUB_ROOT / "data" / "document-index" / "index.jsonl"


def build_path_map(db_path: str) -> dict[int, str]:
    """Build {og_db_id: target_path} from inventory DB, skipping NULL targets."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, target_path FROM documents WHERE target_path IS NOT NULL")
    result = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()
    logger.info("Loaded %d path mappings from inventory DB", len(result))
    return result


def remap_index(
    index_path: str, path_map: dict[int, str], *, dry_run: bool = False
) -> dict[str, int]:
    """Rewrite og_standards paths in index.jsonl using path_map.

    Returns stats dict with remapped, skipped_no_target, non_og, total counts.
    """
    index_p = Path(index_path)
    stats = {"remapped": 0, "skipped_no_target": 0, "non_og": 0, "total": 0}

    if dry_run:
        with open(index_p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                stats["total"] += 1
                if rec.get("source") != "og_standards":
                    stats["non_og"] += 1
                    continue
                db_id = rec.get("og_db_id")
                if db_id and db_id in path_map:
                    stats["remapped"] += 1
                else:
                    stats["skipped_no_target"] += 1
        logger.info(
            "DRY-RUN: %d remapped, %d skipped (no target), %d non-og, %d total",
            stats["remapped"], stats["skipped_no_target"],
            stats["non_og"], stats["total"],
        )
        return stats

    # Live run — backup + atomic rewrite
    backup_path = Path(str(index_p) + ".bak")
    shutil.copy2(index_p, backup_path)
    logger.info("Backup: %s", backup_path)

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=index_p.parent, prefix=".og-remap-", suffix=".jsonl"
    )
    try:
        with os.fdopen(tmp_fd, "w") as out_f, open(index_p) as in_f:
            for line in in_f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                stats["total"] += 1

                if rec.get("source") != "og_standards":
                    stats["non_og"] += 1
                    out_f.write(json.dumps(rec) + "\n")
                    continue

                db_id = rec.get("og_db_id")
                if db_id and db_id in path_map:
                    rec["old_path"] = rec["path"]
                    rec["path"] = path_map[db_id]
                    rec["remapped_by"] = "remap-og-standards-paths"
                    stats["remapped"] += 1
                else:
                    stats["skipped_no_target"] += 1

                out_f.write(json.dumps(rec) + "\n")

                if stats["total"] % 200_000 == 0:
                    logger.info("  ... %d records, %d remapped", stats["total"], stats["remapped"])

        os.replace(tmp_path, index_p)
        logger.info(
            "Done: %d remapped, %d skipped (no target), %d non-og, %d total",
            stats["remapped"], stats["skipped_no_target"],
            stats["non_og"], stats["total"],
        )
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remap og_standards paths using inventory DB target_path"
    )
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to _inventory.db")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="Path to index.jsonl")
    parser.add_argument("--dry-run", action="store_true", help="Report changes, no writes")
    args = parser.parse_args()

    path_map = build_path_map(args.db)
    stats = remap_index(args.index, path_map, dry_run=args.dry_run)

    logger.info("Summary: %s", json.dumps(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
