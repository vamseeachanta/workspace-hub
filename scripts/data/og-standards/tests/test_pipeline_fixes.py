# ABOUTME: Tests for the og-standards pipeline fixes that accompany rename mode (#3886)
# ABOUTME: sha256 column, catalog FTS rebuild, og-ingest flag drift, source roots under raw/

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import yaml

from conftest import PIPELINE_DIR, sha256_of


def _columns(db):
    conn = sqlite3.connect(db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(documents)")]
    conn.close()
    return cols


def test_inventory_fresh_db_records_file_sha256(library, tmp_path):
    from inventory import StandardsInventory

    raw = library["root"] / "raw"
    raw.mkdir()
    pdf = raw / "API Spec 17D.pdf"
    pdf.write_bytes(b"%PDF-1.4 synthetic 17D")
    cfg = yaml.safe_load(library["config"].read_text(encoding="utf-8"))
    cfg["database_path"] = str(tmp_path / "fresh.db")
    cfg_path = tmp_path / "fresh.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    inv = StandardsInventory(str(cfg_path))
    try:
        inv.run_full_scan()
    finally:
        inv.close()

    assert "sha256" in _columns(cfg["database_path"])
    conn = sqlite3.connect(cfg["database_path"])
    (sha,) = conn.execute("SELECT sha256 FROM documents").fetchone()
    conn.close()
    assert sha == sha256_of(pdf)


def test_inventory_migrates_legacy_db_without_data_loss(library):
    from inventory import StandardsInventory

    assert "sha256" not in _columns(library["db"])
    inv = StandardsInventory(str(library["config"]))
    try:
        inv._init_database(force=False)
    finally:
        inv.close()

    assert "sha256" in _columns(library["db"])
    conn = sqlite3.connect(library["db"])
    (count,) = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
    conn.close()
    assert count == 2


def test_inventory_refuses_scan_while_rows_sit_under_stale_roots(library):
    """Rows recorded under a moved root would be re-inserted as new documents
    (inventory keys on file_path), so the scan must stop until they are remapped."""
    from inventory import StandardsInventory, StaleSourceRootsError

    raw = library["root"] / "raw"
    raw.mkdir()
    (raw / "API Spec 6A.pdf").write_bytes(library["untouched"].read_bytes())

    inv = StandardsInventory(str(library["config"]))
    try:
        try:
            inv.run_full_scan()
        except StaleSourceRootsError as exc:
            assert "/old/src" in str(exc)
        else:
            raise AssertionError("scan ran over stale source roots")
    finally:
        inv.close()
    conn = sqlite3.connect(library["db"])
    (count,) = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
    conn.close()
    assert count == 2

    inv = StandardsInventory(str(library["config"]))
    try:
        inv.run_full_scan(allow_stale_roots=True)
    finally:
        inv.close()


def test_og_ingest_passes_only_flags_inventory_accepts():
    from inventory import build_parser

    parser = build_parser()
    known = {opt for action in parser._actions for opt in action.option_strings}
    script = (PIPELINE_DIR / "og-ingest").read_text(encoding="utf-8")
    calls = re.findall(r"python\s+inventory\.py([^\n|&>]*)", script)

    assert calls, "og-ingest no longer calls inventory.py"
    for args in calls:
        for flag in re.findall(r"(--?[A-Za-z][\w-]*)", args):
            assert flag in known, f"og-ingest passes {flag!r}, unknown to inventory.py"


def test_og_ingest_stops_when_inventory_fails():
    """inventory.py exits 2 when its stale-roots guard fires; og-ingest must not
    pipe that away and carry on with extract/embed."""
    script = (PIPELINE_DIR / "og-ingest").read_text(encoding="utf-8")
    assert re.search(r"^set -o pipefail\b", script, re.M)
    lines = [ln for ln in script.splitlines() if re.search(r"python\s+inventory\.py", ln)]
    assert lines
    for ln in lines:
        assert "|| " in ln, f"inventory.py failure ignored: {ln.strip()}"


def test_catalog_fts_survives_rebuild_after_rename(library):
    """INSERT OR REPLACE over an external-content FTS5 table corrupts it once the
    content row has changed; the catalog must rebuild instead."""
    from catalog import CatalogGenerator

    conn = sqlite3.connect(library["db"])
    conn.execute(
        "UPDATE documents SET filename='API RP 2RD (2013 draft).pdf', "
        "title='API RP 2RD 2013 draft' WHERE id=1"
    )
    conn.commit()
    conn.close()

    gen = CatalogGenerator(str(library["config"]))
    gen.connect()
    try:
        gen._build_fts_index()
        gen._build_fts_index()
    finally:
        gen.close()

    conn = sqlite3.connect(library["db"])
    conn.execute(
        "INSERT INTO documents_fts(documents_fts, rank) VALUES('integrity-check', 1)"
    )
    ids = [r[0] for r in conn.execute(
        "SELECT rowid FROM documents_fts WHERE documents_fts MATCH 'draft'"
    )]
    conn.close()
    assert ids == [1]


def test_search_fts_excludes_duplicates(library):
    from search import StandardsSearch

    conn = sqlite3.connect(library["db"])
    conn.execute("UPDATE documents SET is_duplicate=1, duplicate_of=2 WHERE id=1")
    conn.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()

    s = StandardsSearch(str(library["db"]))
    s.connect()
    try:
        hits = s.search_fts("API")
    finally:
        s.close()
    assert [h["id"] for h in hits] == [2]


def test_config_source_roots_live_under_raw():
    cfg = yaml.safe_load((PIPELINE_DIR / "config.yaml").read_text(encoding="utf-8"))
    raw_root = Path(cfg["target_directory"]) / "raw"
    for src in cfg["source_directories"]:
        assert Path(src) == raw_root or raw_root in Path(src).parents, src
