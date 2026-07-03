#!/usr/bin/env python3
"""Drive-local SQLite FTS5 index builder."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = SCRIPT_DIR / "drive-index-config.yaml"
HASH_CHUNK_SIZE = 65536

ASSET_COLUMNS = (
    "id asset_type file_path file_name file_extension file_size content_hash "
    "modified_date source_root discipline project_code folder_phase title description "
    "content_category engineering_domain scan_date extraction_status anonymized_title "
    "language page_count word_count last_extracted status canonical_path"
).split()

CREATE_ASSETS_SQL = """
CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    file_extension TEXT,
    file_size INTEGER DEFAULT 0,
    content_hash TEXT,
    modified_date TEXT,
    source_root TEXT,
    discipline TEXT,
    project_code TEXT,
    folder_phase TEXT,
    title TEXT,
    description TEXT,
    content_category TEXT,
    engineering_domain TEXT,
    scan_date TEXT,
    extraction_status TEXT DEFAULT 'pending',
    anonymized_title TEXT,
    language TEXT DEFAULT 'en',
    page_count INTEGER,
    word_count INTEGER,
    last_extracted TEXT,
    status TEXT DEFAULT 'active',
    canonical_path TEXT
)
"""

UPSERT_SQL = f"""
INSERT INTO assets ({", ".join(ASSET_COLUMNS)})
VALUES ({", ".join("?" for _ in ASSET_COLUMNS)})
ON CONFLICT(file_path) DO UPDATE SET
    file_size=excluded.file_size,
    modified_date=excluded.modified_date,
    scan_date=excluded.scan_date,
    status='active'
"""


@dataclass
class Profile:
    name: str
    roots: list[Path]
    canonical_prefix: str
    db: Path
    excludes: set[str]
    topdir_map: dict[str, dict[str, str]]
    extension_map: dict[str, str]
    defaults: dict[str, str]

    @property
    def root(self) -> Path:
        return self.roots[0]


def load_profile(config_path: Path, drive: str, db_override: Path | None = None) -> Profile:
    data = yaml.safe_load(config_path.read_text()) or {}
    raw = data["drives"][drive]
    classification = raw.get("classification", {})
    roots = raw.get("roots") or [raw["root"]]
    return Profile(
        name=drive,
        roots=[Path(root) for root in roots],
        canonical_prefix=raw["canonical_prefix"].rstrip("/"),
        db=db_override or Path(raw["db"]),
        excludes=set(raw.get("excludes", [])),
        topdir_map=classification.get("topdirs", {}) or {},
        extension_map={k.lower(): v for k, v in (classification.get("extensions", {}) or {}).items()},
        defaults=classification.get("defaults", {}) or {},
    )


def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(CREATE_ASSETS_SQL)
    conn.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS assets_fts USING fts5("
        "title, description, anonymized_title, content=assets, content_rowid=rowid)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS scan_state ("
        "key TEXT PRIMARY KEY, value TEXT, updated_at TEXT NOT NULL)"
    )
    conn.commit()
    return conn


def sanitize_text(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-8", "backslashreplace").decode("utf-8")
    return value


def canonical_path(path: Path, profile: Profile) -> str:
    root = root_for_path(path, profile)
    if len(profile.roots) == 1:
        rel = path.relative_to(root)
        return sanitize_text(profile.canonical_prefix + "/" + rel.as_posix())
    rel = path.relative_to(root)
    return sanitize_text(canonical_root(root, profile) + "/" + rel.as_posix())


def canonical_root(root: Path, profile: Profile) -> str:
    if len(profile.roots) == 1:
        return profile.canonical_prefix
    return sanitize_text(profile.canonical_prefix + "/" + sanitize_text(root.name))


def root_for_path(path: Path, profile: Profile) -> Path:
    for root in profile.roots:
        try:
            path.relative_to(root)
            return root
        except ValueError:
            continue
    raise ValueError(f"{path} is outside profile roots")


def iter_files(root: Path, excludes: set[str]) -> Iterable[Path]:
    def walk(current: Path) -> Iterable[Path]:
        try:
            entries = sorted(os.scandir(current), key=lambda e: sanitize_text(e.name))
        except OSError as exc:
            yield ScanError(current, exc)  # type: ignore[misc]
            return
        for entry in entries:
            name = sanitize_text(entry.name)
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if name not in excludes:
                        yield from walk(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    yield Path(entry.path)
            except OSError as exc:
                yield ScanError(Path(entry.path), exc)  # type: ignore[misc]

    yield from walk(root)


@dataclass
class ScanError:
    path: Path
    error: OSError


def classify(path: Path, profile: Profile) -> dict[str, str | None]:
    rel = path.relative_to(root_for_path(path, profile))
    top = sanitize_text(rel.parts[0]) if rel.parts else ""
    mapped = profile.topdir_map.get(top, {})
    ext = path.suffix.lower()
    return {
        "asset_type": profile.extension_map.get(ext, profile.defaults.get("asset_type", "file")),
        "discipline": mapped.get("discipline", profile.defaults.get("discipline")),
        "engineering_domain": mapped.get("engineering_domain", profile.defaults.get("engineering_domain")),
        "project_code": mapped.get("project_code", profile.defaults.get("project_code")),
        "content_category": mapped.get("content_category", profile.defaults.get("content_category")),
    }


def row_for_file(path: Path, profile: Profile, scan_date: str) -> tuple[Any, ...]:
    stat = path.stat()
    root = root_for_path(path, profile)
    canonical = canonical_path(path, profile)
    rel_parent = sanitize_text(path.parent.relative_to(root).as_posix())
    info = classify(path, profile)
    values = {
        "id": hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32],
        "asset_type": info["asset_type"],
        "file_path": canonical,
        "file_name": sanitize_text(path.name),
        "file_extension": sanitize_text(path.suffix.lower() or None),
        "file_size": stat.st_size,
        "content_hash": None,
        "modified_date": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "source_root": canonical_root(root, profile),
        "discipline": info["discipline"],
        "project_code": info["project_code"],
        "folder_phase": None,
        "title": sanitize_text(path.stem),
        "description": rel_parent if rel_parent != "." else profile.canonical_prefix,
        "content_category": info["content_category"],
        "engineering_domain": info["engineering_domain"],
        "scan_date": scan_date,
        "extraction_status": "pending",
        "anonymized_title": None,
        "language": "en",
        "page_count": None,
        "word_count": None,
        "last_extracted": None,
        "status": "active",
        "canonical_path": canonical,
    }
    return tuple(sanitize_text(values[col]) for col in ASSET_COLUMNS)


def existing_row_state(conn: sqlite3.Connection, row: tuple[Any, ...]) -> tuple[str, bool] | None:
    file_path = row[ASSET_COLUMNS.index("file_path")]
    size = row[ASSET_COLUMNS.index("file_size")]
    mtime = row[ASSET_COLUMNS.index("modified_date")]
    found = conn.execute(
        "SELECT file_size, modified_date, status FROM assets WHERE file_path = ?",
        (file_path,),
    ).fetchone()
    if not found:
        return None
    return found[2], bool(found[0] == size and found[1] == mtime)


def unchanged_active(conn: sqlite3.Connection, row: tuple[Any, ...]) -> bool:
    state = existing_row_state(conn, row)
    return bool(state and state[1] and state[0] == "active")


def execute_many(conn: sqlite3.Connection, rows: list[tuple[Any, ...]]) -> None:
    conn.executemany(UPSERT_SQL, rows)


def write_batch(conn: sqlite3.Connection, rows: list[tuple[Any, ...]]) -> int:
    try:
        execute_many(conn, rows)
        return 0
    except sqlite3.Error:
        errors = 0
        for row in rows:
            try:
                conn.execute(UPSERT_SQL, row)
            except sqlite3.Error:
                errors += 1
        return errors


def set_state(conn: sqlite3.Connection, key: str, value: Any) -> None:
    conn.execute(
        "INSERT INTO scan_state(key, value, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (key, str(value), datetime.now(timezone.utc).isoformat()),
    )


def metadata_pass(
    profile: Profile,
    *,
    batch_size: int,
    limit: int | None = None,
    incremental: bool = False,
    prune: bool = True,
) -> dict[str, int]:
    conn = open_db(profile.db)
    scan_date = datetime.now(timezone.utc).isoformat()
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    seen: set[str] = set()
    batch: list[tuple[Any, ...]] = []
    stats = {"files": 0, "errors": 0, "skipped": 0, "rows_added": 0, "rows_updated": 0, "rows_pruned": 0}
    try:
        for root in profile.roots:
            for item in iter_files(root, profile.excludes):
                if isinstance(item, ScanError):
                    stats["errors"] += 1
                    continue
                try:
                    row = row_for_file(item, profile, scan_date)
                    seen.add(row[ASSET_COLUMNS.index("file_path")])
                    stats["files"] += 1
                    state = existing_row_state(conn, row)
                    if incremental and state and state[1] and state[0] == "active":
                        stats["skipped"] += 1
                    else:
                        if state is None:
                            stats["rows_added"] += 1
                        else:
                            stats["rows_updated"] += 1
                        batch.append(row)
                except OSError:
                    stats["errors"] += 1
                if len(batch) >= batch_size:
                    stats["errors"] += write_batch(conn, batch)
                    conn.commit()
                    set_state(conn, "files_seen", stats["files"])
                    conn.commit()
                    batch.clear()
                if limit is not None and stats["files"] >= limit:
                    break
            if limit is not None and stats["files"] >= limit:
                break
        if batch:
            stats["errors"] += write_batch(conn, batch)
        if prune:
            stats["rows_pruned"] = mark_removed(conn, profile, seen)
        conn.execute("INSERT INTO assets_fts(assets_fts) VALUES('rebuild')")
        stats["duration_seconds"] = int(time.monotonic() - start)
        stats["duration_s"] = stats["duration_seconds"]
        stats["row_count"] = conn.execute("SELECT count(*) FROM assets").fetchone()[0]
        for key, value in stats.items():
            set_state(conn, key, value)
        set_state(conn, "last_scan_date", scan_date)
        conn.commit()
        finished_at = datetime.now(timezone.utc).isoformat()
        write_refresh_state(
            profile,
            {
                "index_id": profile.name,
                "host": os.uname().nodename if hasattr(os, "uname") else "",
                "started_at": started_at,
                "finished_at": finished_at,
                "status": "failed" if stats["errors"] else "ok",
                "row_count": stats["row_count"],
                "rows_added": stats["rows_added"],
                "rows_updated": stats["rows_updated"],
                "rows_pruned": stats["rows_pruned"],
                "duration_s": stats["duration_s"],
                "error": f"{stats['errors']} scan error(s)" if stats["errors"] else None,
            },
        )
        return stats
    finally:
        conn.close()


def write_refresh_state(profile: Profile, payload: dict[str, Any]) -> None:
    state_path = profile.db.parent / "refresh-state.json"
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp_path.replace(state_path)


def local_path_from_canonical(file_path: str, profile: Profile) -> Path:
    for root in profile.roots:
        source_root = canonical_root(root, profile)
        try:
            rel = Path(file_path).relative_to(source_root)
        except ValueError:
            continue
        return root / rel
    return profile.root / Path(file_path).relative_to(profile.canonical_prefix)


def mark_removed(conn: sqlite3.Connection, profile: Profile, seen: set[str]) -> int:
    removed = 0
    for root in profile.roots:
        source_root = canonical_root(root, profile)
        rows = conn.execute(
            "SELECT file_path FROM assets WHERE source_root = ? AND status = 'active'",
            (source_root,),
        ).fetchall()
        for (file_path,) in rows:
            if file_path not in seen:
                conn.execute("UPDATE assets SET status = 'removed' WHERE file_path = ?", (file_path,))
                removed += 1
    return removed


def hash_incremental(profile: Profile, batch_size: int, limit: int | None = None) -> dict[str, int]:
    conn = open_db(profile.db)
    rows = conn.execute(
        "SELECT file_path FROM assets WHERE content_hash IS NULL AND status = 'active' ORDER BY file_size ASC"
    ).fetchall()
    hashed = errors = 0
    try:
        for (file_path,) in rows:
            if limit is not None and hashed >= limit:
                break
            local = local_path_from_canonical(file_path, profile)
            try:
                digest = compute_hash(local)
                conn.execute("UPDATE assets SET content_hash = ? WHERE file_path = ?", (digest, file_path))
                hashed += 1
            except OSError:
                errors += 1
            if hashed and hashed % batch_size == 0:
                conn.commit()
        conn.execute("INSERT INTO assets_fts(assets_fts) VALUES('rebuild')")
        set_state(conn, "hash_files", hashed)
        set_state(conn, "hash_errors", errors)
        conn.commit()
        return {"hashed": hashed, "errors": errors}
    finally:
        conn.close()


def compute_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_SIZE), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def count_walk(profile: Profile) -> int:
    return sum(1 for root in profile.roots for item in iter_files(root, profile.excludes) if not isinstance(item, ScanError))


def reconcile(profile: Profile) -> int:
    conn = open_db(profile.db)
    try:
        walk_count = count_walk(profile)
        roots = [canonical_root(root, profile) for root in profile.roots]
        placeholders = ", ".join("?" for _ in roots)
        db_count = conn.execute(
            f"SELECT count(*) FROM assets WHERE source_root IN ({placeholders}) AND status = 'active'",
            roots,
        ).fetchone()[0]
    finally:
        conn.close()
    delta = db_count - walk_count
    print(f"walk_count={walk_count} db_count={db_count} delta={delta}")
    tolerance = walk_count * 0.001
    return 0 if abs(delta) <= tolerance else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a drive-local SQLite FTS index")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--drive", required=True)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--hash", choices=["none", "incremental"], default="none")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument("--prune", action="store_true")
    parser.add_argument("--batch-size", type=int, default=2000)
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)
    profile = load_profile(args.config, args.drive, args.db)
    if args.reconcile:
        return reconcile(profile)
    if args.hash == "incremental":
        print(hash_incremental(profile, args.batch_size, args.limit))
    else:
        print(metadata_pass(profile, batch_size=args.batch_size, limit=args.limit, incremental=args.incremental, prune=args.prune))
    return 0


if __name__ == "__main__":
    sys.exit(main())
