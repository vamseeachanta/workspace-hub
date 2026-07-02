from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from conftest import make_raw_byte_file, rows


def run_metadata(builder, profile, batch_size=3, limit=None):
    return builder.metadata_pass(profile, batch_size=batch_size, limit=limit)


def test_schema_matches_ace_columns(builder, profile):
    conn = builder.open_db(profile.db)
    try:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(assets)")]
        assert columns == builder.ASSET_COLUMNS
        fts_sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'assets_fts'"
        ).fetchone()[0]
        assert "content='assets'" in fts_sql or "content=assets" in fts_sql
    finally:
        conn.close()


def test_index_row_count_matches_fixture(builder, profile):
    run_metadata(builder, profile)
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE status = 'active'")[0][0] == 9


def test_excludes_recycle_bin_and_svi(builder, profile):
    run_metadata(builder, profile)
    paths = [row[0] for row in rows(profile.db, "SELECT file_path FROM assets")]
    assert not any("$RECYCLE.BIN" in path for path in paths)
    assert not any("System Volume Information" in path for path in paths)


def test_canonical_path_prefix(builder, profile, fixture_tree):
    run_metadata(builder, profile)
    records = rows(profile.db, "SELECT file_path, canonical_path FROM assets")
    assert all(path.startswith("/mnt/dde/") for row in records for path in row)  # abs-path-allowed
    assert all(str(fixture_tree["root"]) not in path for row in records for path in row)


def test_fts_query_hits(builder, profile):
    run_metadata(builder, profile)
    conn = sqlite3.connect(profile.db)
    try:
        hit = conn.execute(
            "SELECT base.file_name FROM assets_fts "
            "JOIN assets base ON base.rowid = assets_fts.rowid "
            "WHERE assets_fts MATCH ?",
            ("riser fatigue",),
        ).fetchone()
    finally:
        conn.close()
    assert hit == ("riser_fatigue_report.pdf",)


def test_idempotent_rerun(builder, profile):
    run_metadata(builder, profile)
    before = rows(profile.db, "SELECT id, file_path FROM assets ORDER BY file_path")
    run_metadata(builder, profile)
    after = rows(profile.db, "SELECT id, file_path FROM assets ORDER BY file_path")
    assert after == before
    path = "/mnt/dde/documents/riser_fatigue_report.pdf"  # abs-path-allowed
    expected = hashlib.sha256(path.encode()).hexdigest()[:32]
    assert dict(after)[expected] == path


def test_resume_after_interrupt_rewalks_from_start(builder, profile):
    run_metadata(builder, profile, batch_size=3, limit=3)
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE status = 'active'")[0][0] == 3
    run_metadata(builder, profile, batch_size=3)
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE status = 'active'")[0][0] == 9
    assert rows(profile.db, "SELECT value FROM scan_state WHERE key = 'files'")[0][0] == "9"


def test_hash_stage_separate_and_incremental(builder, profile):
    run_metadata(builder, profile)
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE content_hash IS NULL")[0][0] == 9
    partial = builder.hash_incremental(profile, batch_size=2, limit=4)
    assert partial["hashed"] == 4
    complete = builder.hash_incremental(profile, batch_size=2)
    assert complete["hashed"] == 5
    missing = rows(profile.db, "SELECT count(*) FROM assets WHERE content_hash IS NULL")[0][0]
    assert missing == 0


def test_unreadable_file_does_not_abort(builder, profile, monkeypatch):
    original = builder.row_for_file

    def fail_once(path, active_profile, scan_date):
        if path.name == "readme.txt":
            raise OSError("simulated unreadable file")
        return original(path, active_profile, scan_date)

    monkeypatch.setattr(builder, "row_for_file", fail_once)
    stats = run_metadata(builder, profile)
    assert stats["errors"] == 1
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE status = 'active'")[0][0] == 8


def test_symlink_skipped(builder, profile):
    run_metadata(builder, profile)
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE file_path LIKE '%/link/%'")[0][0] == 0


def test_reconcile_mode(builder, profile):
    run_metadata(builder, profile)
    assert builder.reconcile(profile) == 0
    conn = sqlite3.connect(profile.db)
    try:
        conn.execute("DELETE FROM assets WHERE file_name = 'readme.txt'")
        conn.commit()
    finally:
        conn.close()
    assert builder.reconcile(profile) != 0


def test_removed_row_reactivated_on_reappearance(builder, profile, fixture_tree):
    target = fixture_tree["root"] / "documents/readme.txt"
    run_metadata(builder, profile)
    target.unlink()
    run_metadata(builder, profile)
    status = rows(profile.db, "SELECT status FROM assets WHERE file_path = ?", ("/mnt/dde/documents/readme.txt",))[0][0]  # abs-path-allowed
    assert status == "removed"
    target.write_text("back")
    run_metadata(builder, profile)
    status = rows(profile.db, "SELECT status FROM assets WHERE file_path = ?", ("/mnt/dde/documents/readme.txt",))[0][0]  # abs-path-allowed
    assert status == "active"


def test_surrogate_filename_batch_fallback(builder, profile, fixture_tree, monkeypatch):
    make_raw_byte_file(fixture_tree["root"])
    calls = {"count": 0}
    original = builder.execute_many

    def fail_first_batch(conn, batch):
        calls["count"] += 1
        if calls["count"] == 1:
            raise sqlite3.ProgrammingError("simulated batch poison")
        return original(conn, batch)

    monkeypatch.setattr(builder, "execute_many", fail_first_batch)
    stats = run_metadata(builder, profile, batch_size=20)
    assert stats["errors"] == 0
    paths = [row[0] for row in rows(profile.db, "SELECT file_path FROM assets")]
    assert any("bad_\\udcff_name.txt" in path for path in paths)
    assert all("\udcff" not in path for path in paths)


def test_classification_map_applied(builder, profile):
    run_metadata(builder, profile)
    row = rows(
        profile.db,
        "SELECT discipline, engineering_domain, asset_type FROM assets WHERE file_path = ?",
        ("/mnt/dde/Orcaflex/model run/sim.dat",),  # abs-path-allowed
    )[0]
    assert row == ("engineering", "offshore_analysis", "data")
