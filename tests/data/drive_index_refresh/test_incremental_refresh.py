from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from drive_index_refresh_helpers import rows


def run_refresh(builder, profile, *, incremental=True, prune=False):
    return builder.metadata_pass(
        profile,
        batch_size=2,
        incremental=incremental,
        prune=prune,
    )


def test_incremental_picks_up_added_file(builder, profile, fixture_tree):
    run_refresh(builder, profile)
    added = fixture_tree["root"] / "root-a" / "new_calc.txt"
    added.write_text("new")

    stats = run_refresh(builder, profile)

    assert stats["rows_added"] == 1
    assert rows(profile.db, "SELECT status FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/new_calc.txt",))[0][0] == "active"  # abs-path-allowed


def test_incremental_updates_modified_file(builder, profile, fixture_tree):
    run_refresh(builder, profile)
    target = fixture_tree["root"] / "root-a" / "alpha.txt"
    before = rows(profile.db, "SELECT file_size, scan_date FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/alpha.txt",))[0]  # abs-path-allowed
    target.write_text("changed content")

    stats = run_refresh(builder, profile)
    after = rows(profile.db, "SELECT file_size, scan_date, status FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/alpha.txt",))[0]  # abs-path-allowed

    assert stats["rows_updated"] == 1
    assert after[0] != before[0]
    assert after[1] != before[1]
    assert after[2] == "active"


def test_incremental_skips_unchanged(builder, profile):
    run_refresh(builder, profile)
    before = rows(profile.db, "SELECT scan_date FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/alpha.txt",))[0][0]  # abs-path-allowed

    stats = run_refresh(builder, profile)

    assert stats["skipped"] == 3
    assert stats["rows_updated"] == 0
    assert rows(profile.db, "SELECT scan_date FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/alpha.txt",))[0][0] == before  # abs-path-allowed


def test_prune_marks_removed_not_deleted(builder, profile, fixture_tree):
    run_refresh(builder, profile)
    (fixture_tree["root"] / "root-a" / "alpha.txt").unlink()

    stats = run_refresh(builder, profile, prune=True)

    assert stats["rows_pruned"] == 1
    assert rows(profile.db, "SELECT status FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/alpha.txt",))[0][0] == "removed"  # abs-path-allowed
    assert rows(profile.db, "SELECT count(*) FROM assets")[0][0] == 3


def test_removed_row_reactivated_on_reappearance(builder, profile, fixture_tree):
    target = fixture_tree["root"] / "root-a" / "alpha.txt"
    run_refresh(builder, profile)
    target.unlink()
    run_refresh(builder, profile, prune=True)
    target.write_text("content root-a/alpha.txt")

    stats = run_refresh(builder, profile)

    assert stats["rows_updated"] == 1
    assert rows(profile.db, "SELECT status FROM assets WHERE file_path = ?", ("/mnt/fixture/root-a/alpha.txt",))[0][0] == "active"  # abs-path-allowed


def test_prune_scoped_to_walked_roots(builder, profile):
    run_refresh(builder, profile)
    conn = sqlite3.connect(profile.db)
    try:
        conn.execute(
            "INSERT INTO assets (id, asset_type, file_path, file_name, source_root, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("external", "file", "/mnt/other/outside.txt", "outside.txt", "/mnt/other", "active"),  # abs-path-allowed
        )
        conn.commit()
    finally:
        conn.close()

    run_refresh(builder, profile, prune=True)

    assert rows(profile.db, "SELECT status FROM assets WHERE file_path = ?", ("/mnt/other/outside.txt",))[0][0] == "active"  # abs-path-allowed


def test_update_preserves_extraction_columns(builder, profile, fixture_tree):
    run_refresh(builder, profile)
    conn = sqlite3.connect(profile.db)
    try:
        conn.execute(
            "UPDATE assets SET title=?, discipline=?, extraction_status=?, content_hash=?, last_extracted=? WHERE file_path=?",
            ("Curated title", "curated", "extracted", "sha256:abc", "2026-01-01", "/mnt/fixture/root-a/alpha.txt"),  # abs-path-allowed
        )
        conn.commit()
    finally:
        conn.close()
    (fixture_tree["root"] / "root-a" / "alpha.txt").write_text("changed")

    run_refresh(builder, profile)

    preserved = rows(
        profile.db,
        "SELECT title, discipline, extraction_status, content_hash, last_extracted FROM assets WHERE file_path=?",
        ("/mnt/fixture/root-a/alpha.txt",),  # abs-path-allowed
    )[0]
    assert preserved == ("Curated title", "curated", "extracted", "sha256:abc", "2026-01-01")


def test_refresh_preserves_foreign_tables(builder, profile):
    conn = builder.open_db(profile.db)
    try:
        conn.execute("CREATE TABLE standards (id TEXT PRIMARY KEY, title TEXT)")
        conn.execute("INSERT INTO standards VALUES ('api', 'API')")
        conn.commit()
    finally:
        conn.close()

    run_refresh(builder, profile)

    assert rows(profile.db, "SELECT title FROM standards WHERE id='api'")[0][0] == "API"


def test_refresh_preserves_legacy_uuid_ids(builder, profile, fixture_tree):
    conn = builder.open_db(profile.db)
    try:
        row = builder.row_for_file(fixture_tree["root"] / "root-a" / "alpha.txt", profile, "old")
        values = dict(zip(builder.ASSET_COLUMNS, row))
        values["id"] = "0d4919d6-1360-4d3d-ac97-ddbd3fb71c4e"
        conn.execute(
            f"INSERT INTO assets ({', '.join(builder.ASSET_COLUMNS)}) VALUES ({', '.join('?' for _ in builder.ASSET_COLUMNS)})",
            tuple(values[col] for col in builder.ASSET_COLUMNS),
        )
        conn.commit()
    finally:
        conn.close()
    (fixture_tree["root"] / "root-a" / "alpha.txt").write_text("changed")

    run_refresh(builder, profile)

    assert rows(profile.db, "SELECT id FROM assets WHERE file_path=?", ("/mnt/fixture/root-a/alpha.txt",))[0][0] == "0d4919d6-1360-4d3d-ac97-ddbd3fb71c4e"  # abs-path-allowed


def test_multi_root_profile(builder, profile):
    run_refresh(builder, profile)
    paths = {row[0] for row in rows(profile.db, "SELECT file_path FROM assets")}
    assert paths == {
        "/mnt/fixture/root-a/alpha.txt",  # abs-path-allowed
        "/mnt/fixture/root-a/riser_vortex.dat",  # abs-path-allowed
        "/mnt/fixture/root-b/beta.pdf",  # abs-path-allowed
    }


def test_multi_root_canonical_path_maps_back_to_local_root(builder, profile, fixture_tree):
    local = builder.local_path_from_canonical("/mnt/fixture/root-b/beta.pdf", profile)  # abs-path-allowed

    assert local == fixture_tree["root"] / "root-b" / "beta.pdf"


def test_fts_synced_after_incremental(builder, profile, fixture_tree):
    run_refresh(builder, profile)
    (fixture_tree["root"] / "root-a" / "vortex_new.txt").write_text("vortex content")
    run_refresh(builder, profile)

    hit = rows(
        profile.db,
        "SELECT base.file_name FROM assets_fts JOIN assets base ON base.rowid = assets_fts.rowid WHERE assets_fts MATCH ?",
        ("vortex",),
    )
    assert ("vortex_new.txt",) in hit


def test_state_file_written_on_success(builder, profile):
    stats = run_refresh(builder, profile)

    state = json.loads((profile.db.parent / "refresh-state.json").read_text())
    assert state["status"] == "ok"
    assert state["row_count"] == 3
    assert state["rows_added"] == stats["rows_added"]
    assert "duration_s" in state
    assert not (profile.db.parent / "refresh-state.json.tmp").exists()


def test_state_file_and_exit_on_failure(builder, tmp_path):
    profile = builder.Profile(
        name="bad",
        roots=[tmp_path / "missing"],
        canonical_prefix="/mnt/bad",  # abs-path-allowed
        db=tmp_path / "index.db",
        excludes=set(),
        topdir_map={},
        extension_map={},
        defaults={},
    )

    stats = builder.metadata_pass(profile, batch_size=1, incremental=True, prune=True)

    assert stats["errors"] == 1
    state = json.loads((profile.db.parent / "refresh-state.json").read_text())
    assert state["status"] == "failed"
    assert state["error"]
