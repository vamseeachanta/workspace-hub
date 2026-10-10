# ABOUTME: Tests for rename.py — carry library renames into the inventory DB, FTS and catalog (#3886)
# ABOUTME: Synthetic fixtures only; never touches a real library or shared drive

from __future__ import annotations

import json
import sqlite3

import pytest

from conftest import write_log


def _row(db, target):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM documents WHERE target_path = ?", (str(target),)
    ).fetchone()
    conn.close()
    return row


def _fts_ids(db, query):
    conn = sqlite3.connect(db)
    ids = [r[0] for r in conn.execute(
        "SELECT rowid FROM documents_fts WHERE documents_fts MATCH ?", (query,)
    )]
    conn.close()
    return ids


def _fts_integrity_ok(db):
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            "INSERT INTO documents_fts(documents_fts, rank) VALUES('integrity-check', 1)"
        )
        return True
    except sqlite3.DatabaseError:
        return False
    finally:
        conn.close()


# --- parse_rename_log -------------------------------------------------------


def test_parse_rename_log_resolves_relative_paths(library, tmp_path):
    from rename import parse_rename_log

    log = write_log(
        tmp_path / "RENAME-LOG.md",
        [
            ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
            (str(library["untouched"]), str(library["untouched"]), "a" * 64),
        ],
    )
    entries = parse_rename_log(log, library_root=library["root"])

    assert len(entries) == 2
    assert entries[0].old_path == str(library["old"])
    assert entries[0].new_path == str(library["new"])
    assert entries[0].sha256 == library["sha"]
    assert entries[1].old_path == str(library["untouched"])


def test_parse_rename_log_missing_sha_raises(library, tmp_path):
    from rename import parse_rename_log

    log = write_log(tmp_path / "RENAME-LOG.md", [("API/a.pdf", "API/b.pdf", "")])
    with pytest.raises(ValueError, match="line 7"):
        parse_rename_log(log, library_root=library["root"])


def test_parse_rename_log_malformed_sha_raises(library, tmp_path):
    from rename import parse_rename_log

    log = write_log(tmp_path / "RENAME-LOG.md", [("API/a.pdf", "API/b.pdf", "abc123")])
    with pytest.raises(ValueError, match="SHA-256"):
        parse_rename_log(log, library_root=library["root"])


def test_parse_rename_log_without_table_raises(library, tmp_path):
    from rename import parse_rename_log

    log = tmp_path / "RENAME-LOG.md"
    log.write_text("# Rename log\n\nnothing here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no rename table"):
        parse_rename_log(log, library_root=library["root"])


# --- apply_renames ------------------------------------------------------------


def _entries(library, tmp_path, rows=None):
    from rename import parse_rename_log

    rows = rows or [
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"])
    ]
    log = write_log(tmp_path / "RENAME-LOG.md", rows)
    return parse_rename_log(log, library_root=library["root"])


def test_apply_renames_updates_row_and_records_sha256(library, tmp_path):
    from rename import apply_renames

    report = apply_renames(library["db"], _entries(library, tmp_path), dry_run=False)

    assert report.applied == 1
    assert _row(library["db"], library["old"]) is None
    row = _row(library["db"], library["new"])
    assert row["filename"] == "API RP 2RD (2013 draft).pdf"
    assert row["title"] == "API RP 2RD (2013 draft)"
    assert row["sha256"] == library["sha"]
    assert row["file_path"] == "/old/src/API RP 2RD (2013).pdf"  # provenance kept
    untouched = _row(library["db"], library["untouched"])
    assert untouched["filename"] == "API Spec 6A.pdf"


def test_apply_renames_dry_run_makes_no_change(library, tmp_path):
    from rename import apply_renames

    before = library["db"].read_bytes()
    report = apply_renames(library["db"], _entries(library, tmp_path), dry_run=True)

    assert report.applied == 0
    assert report.planned == 1
    assert library["db"].read_bytes() == before


def test_apply_renames_rebuilds_fts(library, tmp_path):
    from rename import apply_renames

    assert _fts_ids(library["db"], "draft") == []
    apply_renames(library["db"], _entries(library, tmp_path), dry_run=False)

    row = _row(library["db"], library["new"])
    assert _fts_ids(library["db"], "draft") == [row["id"]]
    assert _fts_integrity_ok(library["db"])


def test_old_path_not_in_db_raises_and_applies_nothing(library, tmp_path):
    from rename import apply_renames

    entries = _entries(
        library,
        tmp_path,
        [
            ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
            ("API/never-catalogued.pdf", "API/API Spec 6A.pdf", "b" * 64),
        ],
    )
    before = library["db"].read_bytes()
    with pytest.raises(ValueError, match="never-catalogued"):
        apply_renames(library["db"], entries, dry_run=False)
    assert library["db"].read_bytes() == before


def test_sha256_mismatch_raises_and_applies_nothing(library, tmp_path):
    from rename import apply_renames

    entries = _entries(
        library,
        tmp_path,
        [("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", "c" * 64)],
    )
    before = library["db"].read_bytes()
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        apply_renames(library["db"], entries, dry_run=False)
    assert library["db"].read_bytes() == before


def test_missing_new_file_raises(library, tmp_path):
    from rename import apply_renames

    library["new"].unlink()
    with pytest.raises(ValueError, match="not found"):
        apply_renames(library["db"], _entries(library, tmp_path), dry_run=False)


def test_new_path_already_owned_by_another_row_raises(library, tmp_path):
    from rename import apply_renames

    sha = library["sha"]
    library["untouched"].write_bytes(library["new"].read_bytes())
    entries = _entries(
        library, tmp_path, [("API/API RP 2RD (2013).pdf", "API/API Spec 6A.pdf", sha)]
    )
    with pytest.raises(ValueError, match="already the target"):
        apply_renames(library["db"], entries, dry_run=False)


def test_rerun_is_idempotent(library, tmp_path):
    from rename import apply_renames

    entries = _entries(library, tmp_path)
    apply_renames(library["db"], entries, dry_run=False)
    report = apply_renames(library["db"], entries, dry_run=False)

    assert report.applied == 0
    assert report.already_applied == 1
    assert _fts_integrity_ok(library["db"])


# --- remap_source_root -------------------------------------------------------


def test_remap_source_root_rewrites_prefix_only_on_boundary(library):
    from rename import remap_source_root

    conn = sqlite3.connect(library["db"])
    conn.execute(
        """INSERT INTO documents (file_path, filename, source_dir, target_path)
           VALUES ('/old/srcX/other.pdf', 'other.pdf', '/old/srcX', NULL)"""
    )
    conn.commit()
    conn.close()

    dry = remap_source_root(library["db"], "/old/src", "/lib/raw", dry_run=True)
    assert dry == 2
    assert _row(library["db"], library["untouched"])["file_path"].startswith("/old/src/")

    changed = remap_source_root(library["db"], "/old/src", "/lib/raw", dry_run=False)
    assert changed == 2
    row = _row(library["db"], library["untouched"])
    assert row["file_path"] == "/lib/raw/API Spec 6A.pdf"
    assert row["source_dir"] == "/lib/raw"
    conn = sqlite3.connect(library["db"])
    other = conn.execute(
        "SELECT file_path, source_dir FROM documents WHERE filename='other.pdf'"
    ).fetchone()
    conn.close()
    assert other == ("/old/srcX/other.pdf", "/old/srcX")


# --- CLI ----------------------------------------------------------------------


def test_main_applies_and_regenerates_catalog(library, tmp_path):
    from rename import main

    write_log(
        library["root"] / "RENAME-LOG.md",
        [("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"])],
    )
    rc = main(["--config", str(library["config"])])

    assert rc == 0
    catalog = json.loads((library["root"] / "_catalog.json").read_text(encoding="utf-8"))
    rel_paths = {d.get("relative_path") for d in catalog["documents"]}
    assert any(p and p.endswith("API RP 2RD (2013 draft).pdf") for p in rel_paths)
    assert not any(p and p.endswith("API RP 2RD (2013).pdf") for p in rel_paths)


def test_main_dry_run_by_flag_writes_nothing(library, tmp_path):
    from rename import main

    write_log(
        library["root"] / "RENAME-LOG.md",
        [("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"])],
    )
    before = library["db"].read_bytes()
    rc = main(["--config", str(library["config"]), "--dry-run"])

    assert rc == 0
    assert library["db"].read_bytes() == before
    assert not (library["root"] / "_catalog.json").exists()


def test_main_returns_nonzero_on_invalid_log(library):
    from rename import main

    write_log(
        library["root"] / "RENAME-LOG.md",
        [("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", "d" * 64)],
    )
    assert main(["--config", str(library["config"]), "--no-catalog"]) == 1
