#!/usr/bin/env python3
# ABOUTME: Tests for remap-og-standards-paths.py — og_standards path fixup (WRK-1254)
# ABOUTME: Verifies DB lookup, index rewriting, and edge cases

"""Tests for the og_standards path remap script."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def db_path(tmp_path):
    """Create a minimal inventory DB with old→new path mappings."""
    db = tmp_path / "_inventory.db"
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            file_path TEXT,
            target_path TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO documents (id, file_path, target_path) VALUES (?, ?, ?)",
        [
            (1, "/mnt/ace/0000 O&G/0000 Codes & Standards/API/API-RP-2A.pdf",
             "/mnt/ace/O&G-Standards/API/API-RP-2A.pdf"),
            (2, "/mnt/ace/0000 O&G/0000 Codes & Standards/DNV/DNV-OS-F101.pdf",
             "/mnt/ace/O&G-Standards/DNV/DNV-OS-F101.pdf"),
            (3, "/mnt/ace/0000 O&G/0000 Codes & Standards/Spare/old-file.pdf",
             None),  # no target_path
            (4, "/mnt/ace/0000 O&G/Oil and Gas Codes/API Standards/API-5L.pdf",
             "/mnt/ace/O&G-Standards/API/API-5L.pdf"),
        ],
    )
    conn.commit()
    conn.close()
    return db


@pytest.fixture
def index_path(tmp_path):
    """Create a test index.jsonl with og_standards entries."""
    idx = tmp_path / "index.jsonl"
    records = [
        {"path": "/mnt/ace/0000 O&G/0000 Codes & Standards/API/API-RP-2A.pdf",
         "source": "og_standards", "og_db_id": 1, "ext": "pdf", "domain": "pipeline"},
        {"path": "/mnt/ace/0000 O&G/0000 Codes & Standards/DNV/DNV-OS-F101.pdf",
         "source": "og_standards", "og_db_id": 2, "ext": "pdf", "domain": "marine"},
        {"path": "/mnt/ace/0000 O&G/0000 Codes & Standards/Spare/old-file.pdf",
         "source": "og_standards", "og_db_id": 3, "ext": "pdf", "domain": "other"},
        {"path": "/mnt/ace/0000 O&G/Oil and Gas Codes/API Standards/API-5L.pdf",
         "source": "og_standards", "og_db_id": 4, "ext": "pdf", "domain": "pipeline"},
        {"path": "/mnt/ace/docs/_standards/ASTM/ASTM-A36.pdf",
         "source": "ace_standards", "ext": "pdf", "domain": "materials"},
    ]
    with open(idx, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return idx


def _load_index(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


class TestBuildPathMap:
    """Test path map construction from inventory DB."""

    def test_loads_target_paths(self, db_path):
        from remap_og_standards_paths import build_path_map
        pmap = build_path_map(str(db_path))
        assert pmap[1] == "/mnt/ace/O&G-Standards/API/API-RP-2A.pdf"
        assert pmap[2] == "/mnt/ace/O&G-Standards/DNV/DNV-OS-F101.pdf"
        assert pmap[4] == "/mnt/ace/O&G-Standards/API/API-5L.pdf"

    def test_skips_null_target_paths(self, db_path):
        from remap_og_standards_paths import build_path_map
        pmap = build_path_map(str(db_path))
        assert 3 not in pmap

    def test_returns_dict(self, db_path):
        from remap_og_standards_paths import build_path_map
        pmap = build_path_map(str(db_path))
        assert isinstance(pmap, dict)
        assert len(pmap) == 3  # 4 rows, 1 NULL target


class TestRemapIndex:
    """Test index rewriting with remapped paths."""

    def test_remaps_og_standards_paths(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        stats = remap_index(str(index_path), pmap, dry_run=False)
        records = _load_index(index_path)
        assert records[0]["path"] == "/mnt/ace/O&G-Standards/API/API-RP-2A.pdf"
        assert records[1]["path"] == "/mnt/ace/O&G-Standards/DNV/DNV-OS-F101.pdf"
        assert records[3]["path"] == "/mnt/ace/O&G-Standards/API/API-5L.pdf"

    def test_preserves_non_og_standards(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        remap_index(str(index_path), pmap, dry_run=False)
        records = _load_index(index_path)
        ace = [r for r in records if r["source"] == "ace_standards"]
        assert len(ace) == 1
        assert ace[0]["path"] == "/mnt/ace/docs/_standards/ASTM/ASTM-A36.pdf"

    def test_skips_missing_db_id(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        remap_index(str(index_path), pmap, dry_run=False)
        records = _load_index(index_path)
        # Record with og_db_id=3 (no target_path) keeps old path
        spare = [r for r in records if r.get("og_db_id") == 3]
        assert len(spare) == 1
        assert "Spare" in spare[0]["path"]

    def test_stats_correct(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        stats = remap_index(str(index_path), pmap, dry_run=False)
        assert stats["remapped"] == 3
        assert stats["skipped_no_target"] == 1
        assert stats["non_og"] == 1
        assert stats["total"] == 5

    def test_dry_run_no_changes(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        original = _load_index(index_path)
        stats = remap_index(str(index_path), pmap, dry_run=True)
        after = _load_index(index_path)
        assert original == after
        assert stats["remapped"] == 3

    def test_preserves_all_fields(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        original = _load_index(index_path)
        remap_index(str(index_path), pmap, dry_run=False)
        updated = _load_index(index_path)
        for orig, upd in zip(original, updated):
            for key in orig:
                if key == "path" and orig["source"] == "og_standards":
                    continue
                if key in ("remapped_by", "old_path"):
                    continue
                assert upd.get(key) == orig.get(key), f"Field {key} changed"

    def test_creates_backup(self, db_path, index_path):
        from remap_og_standards_paths import build_path_map, remap_index
        pmap = build_path_map(str(db_path))
        remap_index(str(index_path), pmap, dry_run=False)
        bak = Path(str(index_path) + ".bak")
        assert bak.exists()
