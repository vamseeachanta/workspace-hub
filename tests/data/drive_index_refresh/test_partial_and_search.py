"""Refresh regressions use only temporary trees and SQLite databases."""
from __future__ import annotations

import json
import sqlite3

import pytest

from drive_index_refresh_helpers import rows


def state(profile):
    return json.loads((profile.db.parent / "refresh-state.json").read_text())


@pytest.mark.parametrize("batch_size", [1, 100])
def test_one_scan_error_keeps_rows_and_records_partial(builder, profile, monkeypatch, batch_size):
    original = builder.iter_files
    blocked = profile.roots[0] / "blocked"

    def scan(root, excludes):
        yield from original(root, excludes)
        if root == profile.roots[0]:
            yield builder.ScanError(blocked, PermissionError("access denied"))

    monkeypatch.setattr(builder, "iter_files", scan)
    stats = builder.metadata_pass(profile, batch_size=batch_size, incremental=True, prune=True)

    assert stats["errors"] == 1
    assert rows(profile.db, "SELECT count(*) FROM assets")[0][0] == 3
    payload = state(profile)
    assert payload["status"] == "partial"
    assert payload["error_count"] == 1
    assert payload["scan_errors"] == [{"path": str(blocked), "reason": "access denied"}]
    logged = [json.loads(line) for line in (profile.db.parent / "refresh-errors.jsonl").read_text().splitlines()]
    assert logged[-1]["path"] == str(blocked)
    assert logged[-1]["reason"] == "access denied"


@pytest.mark.parametrize("failure", ["walk", "stat"])
def test_scan_error_preserves_unseen_existing_rows(builder, profile, monkeypatch, failure):
    builder.metadata_pass(profile, batch_size=2)
    (profile.roots[1] / "beta.pdf").write_text("changed synthetic content")
    if failure == "walk":
        original = builder.iter_files

        def scan(root, excludes):
            if root == profile.roots[0]:
                yield builder.ScanError(root, PermissionError("access denied"))
            else:
                yield from original(root, excludes)

        monkeypatch.setattr(builder, "iter_files", scan)
    else:
        original = builder.row_for_file

        def scan(path, active_profile, scan_date):
            if path.name == "alpha.txt":
                raise OSError("stat unavailable")
            return original(path, active_profile, scan_date)

        monkeypatch.setattr(builder, "row_for_file", scan)
    stats = builder.metadata_pass(profile, batch_size=2, incremental=True, prune=True)
    assert stats["rows_pruned"] == 0
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE status='active'")[0][0] == 3
    assert state(profile)["status"] == "partial"
    assert len(state(profile)["scan_errors"]) == 1


def test_failed_scan_writes_nothing_even_with_existing_rows(builder, profile, monkeypatch):
    builder.metadata_pass(profile, batch_size=2)

    def scan(root, excludes):
        yield builder.ScanError(root, OSError("unavailable"))

    monkeypatch.setattr(builder, "iter_files", scan)
    stats = builder.metadata_pass(profile, batch_size=2, incremental=True, prune=True)
    assert stats["rows_pruned"] == 0
    assert state(profile)["status"] == "failed"
    assert state(profile)["error_count"] == len(profile.roots)
    assert rows(profile.db, "SELECT count(*) FROM assets WHERE status='active'")[0][0] == 3


@pytest.mark.parametrize("reject_all", [True, False])
def test_row_write_errors_count_only_successful_writes(builder, profile, reject_all):
    conn = builder.open_db(profile.db)
    try:
        condition = "1" if reject_all else "NEW.file_name = 'alpha.txt'"
        conn.execute(
            f"CREATE TRIGGER reject_asset BEFORE INSERT ON assets WHEN {condition} "
            "BEGIN SELECT RAISE(ABORT, 'synthetic rejection'); END"
        )
        conn.commit()
    finally:
        conn.close()
    stats = builder.metadata_pass(profile, batch_size=100, prune=True)
    expected = 0 if reject_all else 2
    assert stats["rows_added"] == expected
    assert stats["errors"] == 3 - expected
    assert rows(profile.db, "SELECT count(*) FROM assets")[0][0] == expected
    payload = state(profile)
    assert payload["status"] == ("failed" if reject_all else "partial")
    assert len(payload["scan_errors"]) == 3 - expected
    assert all(error["reason"] == "synthetic rejection" for error in payload["scan_errors"])


def test_recovery_clears_latest_errors_and_resumes_pruning(builder, profile, monkeypatch):
    original = builder.iter_files
    blocked = profile.roots[0] / "blocked"

    def scan(root, excludes):
        yield from original(root, excludes)
        if root == profile.roots[0]:
            yield builder.ScanError(blocked, OSError("unavailable"))

    with monkeypatch.context() as patch:
        patch.setattr(builder, "iter_files", scan)
        builder.metadata_pass(profile, batch_size=2, prune=True)
        # Only unchanged rows are scanned; no asset write succeeds this time.
        builder.metadata_pass(profile, batch_size=2, incremental=True, prune=True)
        assert state(profile)["status"] == "failed"
    removed = profile.roots[0] / "alpha.txt"
    removed.unlink()
    stats = builder.metadata_pass(profile, batch_size=2, incremental=True, prune=True)
    assert stats["rows_pruned"] == 1
    assert state(profile)["status"] == "ok"
    assert state(profile)["error_count"] == 0
    assert state(profile)["scan_errors"] == []
    assert len((profile.db.parent / "refresh-errors.jsonl").read_text().splitlines()) == 2


def test_fts_migration_rebuilds_existing_rows_without_scan(builder, profile, multi_root_config, monkeypatch):
    canonical = str(profile.roots[0] / "folderneedle" / "48219" / "fileneedle.pdf")
    with sqlite3.connect(profile.db) as conn:
        conn.execute(builder.CREATE_ASSETS_SQL)
        conn.execute("CREATE VIRTUAL TABLE assets_fts USING fts5(title, description, anonymized_title, content=assets, content_rowid=rowid)")
        conn.execute(
            "INSERT INTO assets(id, asset_type, file_path, file_name, title, description, anonymized_title) VALUES(?, ?, ?, ?, ?, ?, ?)",
            ("legacy", "file", canonical, "fileneedle.pdf", "curated", "summary", "anonymous"),
        )
        conn.execute("INSERT INTO assets_fts(assets_fts) VALUES('rebuild')")
        before = conn.execute("SELECT * FROM assets").fetchall()

    def no_scan(*args, **kwargs):
        pytest.fail("FTS migration must not scan files")

    monkeypatch.setattr(builder, "iter_files", no_scan)
    monkeypatch.setattr(builder, "row_for_file", no_scan)
    assert builder.main([
        "--config", str(multi_root_config), "--drive", "fixture", "--rebuild-fts",
    ]) == 0
    for _ in range(2):
        conn = builder.open_db(profile.db)
        try:
            for query in [
                'file_path:folderneedle', 'file_path:48219',
                'file_name:"fileneedle.pdf"', 'title:curated',
                'description:summary', 'anonymized_title:anonymous',
            ]:
                assert conn.execute("SELECT rowid FROM assets_fts WHERE assets_fts MATCH ?", (query,)).fetchall() == [(1,)]
            assert conn.execute("SELECT * FROM assets").fetchall() == before
        finally:
            conn.close()


def test_refresh_indexes_path_and_filename_after_curated_title(builder, profile):
    builder.metadata_pass(profile, batch_size=2)
    with sqlite3.connect(profile.db) as conn:
        conn.execute("UPDATE assets SET title='curated', description='summary'")
    builder.metadata_pass(profile, batch_size=2, incremental=True)
    assert rows(profile.db, "SELECT rowid FROM assets_fts WHERE assets_fts MATCH ?", ('file_name:"alpha.txt"',))
    assert rows(profile.db, "SELECT rowid FROM assets_fts WHERE assets_fts MATCH ?", ('file_path:"root-a"',))
