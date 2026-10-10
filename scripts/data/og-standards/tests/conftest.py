# ABOUTME: Shared fixtures for og-standards pipeline tests (#3886)
# ABOUTME: Builds a synthetic library, config and inventory DB under tmp_path

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

import pytest
import yaml

PIPELINE_DIR = Path(__file__).resolve().parents[1]
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def library(tmp_path):
    """Synthetic library: one renamed file, one untouched file, a legacy DB.

    The DB mirrors the post-consolidation state: ``target_path`` still holds the
    name the file had before it was renamed on disk.
    """
    root = tmp_path / "O&G-Standards"
    (root / "API").mkdir(parents=True)
    renamed_new = root / "API" / "API RP 2RD (2013 draft).pdf"
    renamed_new.write_bytes(b"%PDF-1.4 synthetic draft body")
    renamed_old = root / "API" / "API RP 2RD (2013).pdf"  # no longer on disk
    untouched = root / "API" / "API Spec 6A.pdf"
    untouched.write_bytes(b"%PDF-1.4 synthetic spec body")

    db = root / "_inventory.db"
    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            extension TEXT,
            file_size INTEGER,
            modified_date TEXT,
            content_hash TEXT,
            organization TEXT,
            doc_type TEXT,
            doc_number TEXT,
            title TEXT,
            source_dir TEXT,
            is_duplicate INTEGER DEFAULT 0,
            duplicate_of INTEGER,
            target_path TEXT,
            processed INTEGER DEFAULT 0,
            scan_date TEXT
        )
        """
    )
    rows = [
        ("/old/src/API RP 2RD (2013).pdf", renamed_old, "/old/src"),
        ("/old/src/API Spec 6A.pdf", untouched, "/old/src"),
    ]
    for file_path, target, source_dir in rows:
        conn.execute(
            """INSERT INTO documents (file_path, filename, extension, content_hash,
                   organization, doc_type, doc_number, title, source_dir, target_path)
               VALUES (?, ?, '.pdf', 'legacy-hash', 'API', 'RP', '2RD', ?, ?, ?)""",
            (file_path, target.name, target.stem, source_dir, str(target)),
        )
    conn.execute(
        """CREATE VIRTUAL TABLE documents_fts USING fts5(
               filename, title, organization, doc_type, doc_number,
               content='documents', content_rowid='id')"""
    )
    conn.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()

    config = tmp_path / "config.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "source_directories": [str(root / "raw")],
                "target_directory": str(root),
                "database_path": str(db),
                "catalog_json": str(root / "_catalog.json"),
                "catalog_html": str(root / "_catalog.html"),
                "file_extensions": [".pdf"],
                "exclude_patterns": [],
                "organization_mappings": {"API": {"patterns": ["API*"]}},
            }
        ),
        encoding="utf-8",
    )
    return {
        "root": root,
        "db": db,
        "config": config,
        "old": renamed_old,
        "new": renamed_new,
        "untouched": untouched,
        "sha": sha256_of(renamed_new),
    }


def write_log(path: Path, rows: list[tuple[str, str, str]]) -> Path:
    lines = [
        "# Rename log",
        "",
        "Files renamed with no content change.",
        "",
        "| Old path | New path | SHA-256 |",
        "|---|---|---|",
    ]
    lines += [f"| `{old}` | `{new}` | {sha} |" for old, new, sha in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
