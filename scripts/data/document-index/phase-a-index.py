#!/usr/bin/env python3
# ABOUTME: Phase A — Multi-source document index builder for WRK-309 document intelligence
# ABOUTME: Scans all document sources in parallel and writes index.jsonl (resume-safe)

"""
Usage:
    python phase-a-index.py [--config config.yaml] [--force] [--source SOURCE] [--dry-run]
"""

import argparse
import hashlib
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_CONFIG = SCRIPT_DIR / "config.yaml"
HASH_CHUNK_SIZE = 65536
PROGRESS_INTERVAL = 1000


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate pipeline configuration."""
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    if "sources" not in cfg:
        raise ValueError("Config missing 'sources' section")
    return cfg


def load_existing_index(index_path: Path) -> Dict[str, Dict]:
    """Load existing index records keyed by path for resume support."""
    existing: Dict[str, Dict] = {}
    if not index_path.exists():
        return existing
    with open(index_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                existing[rec["path"]] = rec
            except (json.JSONDecodeError, KeyError):
                continue
    logger.info("Loaded %d existing index entries", len(existing))
    return existing


def get_existing_hashes(existing: Dict[str, Dict]) -> Set[str]:
    """Extract content hashes from existing records for dedup."""
    hashes: Set[str] = set()
    for rec in existing.values():
        h = rec.get("content_hash")
        if h:
            hashes.add(h)
    return hashes


def matches_exclusion(path_str: str, patterns: List[str]) -> bool:
    """Check if a path matches any exclusion pattern."""
    for pat in patterns:
        if fnmatch(path_str, pat) or fnmatch(os.path.basename(path_str), pat):
            return True
    return False


def compute_sha256(file_path: str) -> Optional[str]:
    """Compute SHA-256 hash of file content."""
    try:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(HASH_CHUNK_SIZE):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"
    except OSError:
        return None


def scan_og_standards(
    source_cfg: Dict, existing: Dict[str, Dict], exclude_patterns: List[str],
) -> List[Dict]:
    """Query og_standards SQLite database for indexed documents."""
    db_path = source_cfg.get("db_path")
    if not db_path or not Path(db_path).exists():
        logger.warning("OG Standards DB not found: %s", db_path)
        return []

    host = source_cfg.get("host", "ace-linux-1")
    records: List[Dict] = []

    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, file_path, filename, extension, file_size, "
            "modified_date, content_hash, organization, doc_type, "
            "doc_number, title, is_duplicate FROM documents"
        )
        for row in cursor:
            fpath = row["file_path"]
            if fpath in existing:
                continue
            if matches_exclusion(fpath, exclude_patterns):
                continue

            size_bytes = row["file_size"] or 0
            content_hash = row["content_hash"]
            if content_hash and not content_hash.startswith("sha256:"):
                content_hash = f"sha256:{content_hash}"

            rec = {
                "path": fpath,
                "host": host,
                "source": "og_standards",
                "ext": (row["extension"] or "").lstrip("."),
                "size_mb": round(size_bytes / (1024 * 1024), 3),
                "mtime": row["modified_date"] or "",
                "content_hash": content_hash,
                "og_db_id": row["id"],
                "org": row["organization"],
                "doc_number": row["doc_number"],
                "is_cad": False,
                "domain": None,
                "summary": None,
            }
            records.append(rec)
    finally:
        conn.close()

    logger.info("og_standards: %d records", len(records))
    return records


def scan_filesystem_source(
    source_cfg: Dict,
    source_name: str,
    existing: Dict[str, Dict],
    seen_hashes: Set[str],
    cad_extensions: List[str],
    exclude_patterns: List[str],
) -> List[Dict]:
    """Walk filesystem paths and build index records."""
    host = source_cfg.get("host", "ace-linux-1")
    valid_exts = set(source_cfg.get("extensions", []))
    records: List[Dict] = []
    count = 0

    for base_path_str in source_cfg.get("paths", []):
        base_path = Path(base_path_str)
        if not base_path.exists():
            logger.warning("Source path not found: %s", base_path)
            continue

        logger.info("Scanning: %s", base_path)
        for root, _dirs, files in os.walk(base_path, followlinks=False):
            if matches_exclusion(root, exclude_patterns):
                continue
            for fname in files:
                fpath = os.path.join(root, fname)
                ext = os.path.splitext(fname)[1].lower()

                if valid_exts and ext not in valid_exts:
                    continue
                if matches_exclusion(fpath, exclude_patterns):
                    continue
                if fpath in existing:
                    continue

                count += 1
                if count % PROGRESS_INTERVAL == 0:
                    logger.info(
                        "%s: scanned %d files, %d indexed",
                        source_name, count, len(records),
                    )

                try:
                    stat = os.stat(fpath)
                except OSError:
                    continue

                is_cad = ext in cad_extensions
                content_hash = None if is_cad else compute_sha256(fpath)

                if content_hash and content_hash in seen_hashes:
                    rec = {
                        "path": fpath,
                        "host": host,
                        "source": source_name,
                        "ext": ext.lstrip("."),
                        "size_mb": round(stat.st_size / (1024 * 1024), 3),
                        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
                        "content_hash": content_hash,
                        "is_cad": is_cad,
                        "domain": None,
                        "summary": None,
                        "duplicate_of": None,
                    }
                    records.append(rec)
                    continue

                mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
                rec = {
                    "path": fpath,
                    "host": host,
                    "source": source_name,
                    "ext": ext.lstrip("."),
                    "size_mb": round(stat.st_size / (1024 * 1024), 3),
                    "mtime": mtime_str,
                    "content_hash": content_hash,
                    "is_cad": is_cad,
                    "domain": None,
                    "summary": None,
                }
                records.append(rec)
                if content_hash:
                    seen_hashes.add(content_hash)

    logger.info("%s: %d records from %d files", source_name, len(records), count)
    return records


def scan_api_metadata(
    source_cfg: Dict, existing: Dict[str, Dict],
) -> List[Dict]:
    """Emit structured records for API data sources."""
    records: List[Dict] = []
    for api in source_cfg.get("apis", []):
        key = f"api://{api['repo']}/{api['api']}"
        if key in existing:
            continue
        rec = {
            "path": key,
            "host": "remote",
            "source": "api_metadata",
            "ext": "api",
            "size_mb": 0,
            "mtime": None,
            "content_hash": None,
            "is_cad": False,
            "domain": None,
            "summary": None,
            "api_name": api.get("api", ""),
            "api_repo": api.get("repo", ""),
            "api_auth": api.get("auth", ""),
            "url_pattern": api.get("url_pattern", ""),
        }
        records.append(rec)
    logger.info("api_metadata: %d records", len(records))
    return records


def deduplicate_records(
    records: List[Dict], seen_hashes: Set[str],
) -> List[Dict]:
    """Mark duplicate records based on content_hash."""
    hash_to_path: Dict[str, str] = {}
    for h in seen_hashes:
        hash_to_path[h] = "existing"

    for rec in records:
        h = rec.get("content_hash")
        if not h:
            continue
        if h in hash_to_path and hash_to_path[h] != "existing":
            rec["duplicate_of"] = hash_to_path[h]
        elif h not in hash_to_path:
            hash_to_path[h] = rec["path"]
    return records


def write_index(
    index_path: Path, existing: Dict[str, Dict], new_records: List[Dict],
    force: bool,
) -> int:
    """Write combined index to JSONL file. Returns total record count."""
    if force:
        merged = {}
    else:
        merged = dict(existing)

    for rec in new_records:
        merged[rec["path"]] = rec

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        for rec in merged.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return len(merged)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase A: Multi-source document index (WRK-309)"
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG, help="Config YAML"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing index instead of resume",
    )
    parser.add_argument("--source", help="Scan only this source (default: all)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Scan but don't write"
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    index_path = HUB_ROOT / cfg["output"]["index_path"]
    exclude_patterns = cfg.get("exclude_patterns", [])
    cad_extensions = cfg.get("cad_extensions", [])

    existing: Dict[str, Dict] = {}
    if not args.force:
        existing = load_existing_index(index_path)
    seen_hashes = get_existing_hashes(existing)

    all_new: List[Dict] = []

    for name, source_cfg in cfg["sources"].items():
        if not source_cfg.get("enabled", False):
            continue
        if args.source and name != args.source:
            continue

        logger.info("Processing source: %s", name)
        stype = source_cfg.get("source_type", name)

        if stype == "og_standards":
            records = scan_og_standards(source_cfg, existing, exclude_patterns)
        elif stype == "api_metadata":
            records = scan_api_metadata(source_cfg, existing)
        else:
            records = scan_filesystem_source(
                source_cfg, name, existing, seen_hashes,
                cad_extensions, exclude_patterns,
            )
        all_new.extend(records)

    all_new = deduplicate_records(all_new, seen_hashes)
    logger.info("Total new/updated records: %d", len(all_new))

    if args.dry_run:
        logger.info("Dry run -- not writing index")
        for rec in all_new[:10]:
            print(json.dumps(rec, indent=2))
        return 0

    total = write_index(index_path, existing, all_new, args.force)
    logger.info("Index written: %s (%d total records)", index_path, total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
