# ABOUTME: Tests for rename.py — carry library renames into the inventory DB, FTS and catalog (#3886)
# ABOUTME: Synthetic fixtures only; never touches a real library or shared drive

from __future__ import annotations

import json
import random
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


def _target_for_id(db, row_id):
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT target_path FROM documents WHERE id = ?", (row_id,)).fetchone()
    conn.close()
    return row[0] if row else None


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


def test_cumulative_log_with_second_rename_applies_and_reruns(library, tmp_path):
    """The log is append-only: A->B applied earlier, B->C appended later."""
    from rename import apply_renames

    apply_renames(library["db"], _entries(library, tmp_path), dry_run=False)
    final = library["root"] / "API" / "API RP 2RD (2013 draft rev).pdf"
    library["new"].rename(final)
    rows = [
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
        ("API/API RP 2RD (2013 draft).pdf", "API/API RP 2RD (2013 draft rev).pdf",
         library["sha"]),
    ]
    report = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert report.applied == 1
    assert _row(library["db"], final)["sha256"] == library["sha"]

    again = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert again.applied == 0


def test_chain_in_one_log_applies_to_final_path(library, tmp_path):
    from rename import apply_renames

    final = library["root"] / "API" / "API RP 2RD (2013 draft rev).pdf"
    library["new"].rename(final)
    rows = [
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
        ("API/API RP 2RD (2013 draft).pdf", "API/API RP 2RD (2013 draft rev).pdf",
         library["sha"]),
    ]
    report = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert report.applied == 1
    assert _row(library["db"], library["old"]) is None
    assert _row(library["db"], final) is not None


def test_swap_through_temp_name_rerun_is_noop(library, tmp_path):
    """A->T, B->A, T->B swaps two files; a re-run must not swap the rows back."""
    from rename import apply_renames

    a, b = library["root"] / "API" / "a.pdf", library["root"] / "API" / "b.pdf"
    a.write_bytes(b"content-a")
    b.write_bytes(b"content-b")
    conn = sqlite3.connect(library["db"])
    conn.execute("UPDATE documents SET target_path=? WHERE id=1", (str(a),))
    conn.execute("UPDATE documents SET target_path=? WHERE id=2", (str(b),))
    conn.commit()
    conn.close()
    from conftest import sha256_of
    sha_a, sha_b = sha256_of(a), sha256_of(b)
    # perform the swap on disk
    a.rename(library["root"] / "API" / "t.pdf")
    b.rename(a)
    (library["root"] / "API" / "t.pdf").rename(b)
    rows = [("API/a.pdf", "API/t.pdf", sha_a), ("API/b.pdf", "API/a.pdf", sha_b),
            ("API/t.pdf", "API/b.pdf", sha_a)]

    first = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert first.applied == 2
    assert _row(library["db"], b)["id"] == 1
    assert _row(library["db"], a)["id"] == 2

    again = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert again.applied == 0
    assert _row(library["db"], b)["id"] == 1
    assert _row(library["db"], a)["id"] == 2


def test_identical_digest_swap_rerun_preserves_row_identity(library, tmp_path):
    """Replay of a temp-name swap must not use SHA equality as row identity."""
    from conftest import sha256_of
    from rename import apply_renames

    a, b = library["root"] / "API" / "a.pdf", library["root"] / "API" / "b.pdf"
    a.write_bytes(b"same-bytes")
    b.write_bytes(b"same-bytes")
    conn = sqlite3.connect(library["db"])
    conn.execute("UPDATE documents SET target_path=? WHERE id=1", (str(a),))
    conn.execute("UPDATE documents SET target_path=? WHERE id=2", (str(b),))
    conn.commit()
    conn.close()
    sha = sha256_of(a)

    a.rename(library["root"] / "API" / "t.pdf")
    b.rename(a)
    (library["root"] / "API" / "t.pdf").rename(b)
    rows = [
        ("API/a.pdf", "API/t.pdf", sha),
        ("API/b.pdf", "API/a.pdf", sha),
        ("API/t.pdf", "API/b.pdf", sha),
    ]

    first = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert first.applied == 2
    assert _row(library["db"], b)["id"] == 1
    assert _row(library["db"], a)["id"] == 2

    again = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert again.applied == 0
    assert _row(library["db"], b)["id"] == 1
    assert _row(library["db"], a)["id"] == 2


def test_name_reused_later_in_log_is_accepted(library, tmp_path):
    from rename import apply_renames

    rows = [
        ("API/API RP 2RD (2013).pdf", "API/tmp.pdf", library["sha"]),
        ("API/tmp.pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
    ]
    report = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert report.applied == 1
    rows.append(("API/API RP 2RD (2013 draft).pdf", "API/tmp.pdf", library["sha"]))
    library["new"].rename(library["root"] / "API" / "tmp.pdf")
    report = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert report.applied == 1
    assert _row(library["db"], library["root"] / "API" / "tmp.pdf") is not None


def test_replay_allows_intermediate_name_reused_by_another_document(library, tmp_path):
    from conftest import sha256_of
    from rename import apply_renames

    a = library["root"] / "API" / "a.pdf"
    b = library["root"] / "API" / "b.pdf"
    c = library["root"] / "API" / "c.pdf"
    d = library["root"] / "API" / "d.pdf"
    a.write_bytes(b"content-x")
    c.write_bytes(b"content-x")
    b.write_bytes(b"content-y")
    conn = sqlite3.connect(library["db"])
    conn.execute("UPDATE documents SET target_path=? WHERE id=1", (str(a),))
    conn.execute("UPDATE documents SET target_path=? WHERE id=2", (str(d),))
    conn.commit()
    conn.close()
    sha_x, sha_y = sha256_of(a), sha256_of(b)
    rows = [
        ("API/a.pdf", "API/b.pdf", sha_x),
        ("API/b.pdf", "API/c.pdf", sha_x),
        ("API/d.pdf", "API/b.pdf", sha_y),
    ]

    first = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert first.applied == 2
    assert _row(library["db"], c)["id"] == 1
    assert _row(library["db"], b)["id"] == 2

    again = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert again.applied == 0
    assert _row(library["db"], c)["id"] == 1
    assert _row(library["db"], b)["id"] == 2


def test_repeated_triple_reversal_keeps_database_at_on_disk_name(library, tmp_path):
    """A->B history must not make a later A->B occurrence undo a B->A replay."""
    from rename import apply_renames

    rows = [
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
    ]
    apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)

    rows.extend([
        ("API/API RP 2RD (2013 draft).pdf", "API/API RP 2RD (2013).pdf", library["sha"]),
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
    ])
    report = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)

    assert report.applied == 0
    assert _target_for_id(library["db"], 1) == str(library["new"])
    again = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert again.applied == 0
    assert _target_for_id(library["db"], 1) == str(library["new"])


def test_repeated_triple_after_applied_revert_moves_database_to_on_disk_name(
    library, tmp_path
):
    """The second A->B occurrence is a distinct log event after A->B, B->A."""
    from rename import apply_renames

    rows = [
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"]),
    ]
    apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    library["new"].rename(library["old"])
    rows.append(
        ("API/API RP 2RD (2013 draft).pdf", "API/API RP 2RD (2013).pdf", library["sha"])
    )
    apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert _target_for_id(library["db"], 1) == str(library["old"])

    library["old"].rename(library["new"])
    rows.append(
        ("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"])
    )
    report = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)

    assert report.applied == 1
    assert _target_for_id(library["db"], 1) == str(library["new"])
    again = apply_renames(library["db"], _entries(library, tmp_path, rows), dry_run=False)
    assert again.applied == 0
    assert _target_for_id(library["db"], 1) == str(library["new"])


def test_random_rename_revert_replays_match_disk_and_second_run_is_noop(
    library, tmp_path
):
    from conftest import sha256_of
    from rename import apply_renames

    rng = random.Random(3886)
    api_dir = library["root"] / "API"
    names = {
        1: [api_dir / "row-1-a.pdf", api_dir / "row-1-b.pdf"],
        2: [api_dir / "row-2-a.pdf", api_dir / "row-2-b.pdf"],
        3: [api_dir / "row-3-a.pdf", api_dir / "row-3-b.pdf"],
    }
    contents = {1: b"row-one", 2: b"row-two", 3: b"row-three"}
    for row_id, paths in names.items():
        paths[0].write_bytes(contents[row_id])
        if paths[1].exists():
            paths[1].unlink()

    conn = sqlite3.connect(library["db"])
    for row_id in (1, 2):
        conn.execute(
            "UPDATE documents SET target_path = ?, filename = ? WHERE id = ?",
            (str(names[row_id][0]), names[row_id][0].name, row_id),
        )
    conn.execute(
        """INSERT INTO documents (id, file_path, filename, extension, content_hash,
               organization, doc_type, doc_number, title, source_dir, target_path)
           VALUES (3, '/old/src/row-3-a.pdf', 'row-3-a.pdf', '.pdf',
               'legacy-hash', 'API', 'RP', '3', 'row-3-a', '/old/src', ?)""",
        (str(names[3][0]),),
    )
    conn.commit()
    conn.close()

    current_index = {1: 0, 2: 0, 3: 0}
    shas = {row_id: sha256_of(paths[0]) for row_id, paths in names.items()}
    log_rows = []

    for _ in range(18):
        row_id = rng.choice([1, 2, 3])
        old = names[row_id][current_index[row_id]]
        current_index[row_id] = 1 - current_index[row_id]
        new = names[row_id][current_index[row_id]]
        old.rename(new)
        log_rows.append((
            old.relative_to(library["root"]).as_posix(),
            new.relative_to(library["root"]).as_posix(),
            shas[row_id],
        ))

        report = apply_renames(
            library["db"], _entries(library, tmp_path, log_rows), dry_run=False
        )
        assert report.applied in (0, 1)
        for check_id, check_paths in names.items():
            assert _target_for_id(library["db"], check_id) == str(
                check_paths[current_index[check_id]]
            )

        again = apply_renames(
            library["db"], _entries(library, tmp_path, log_rows), dry_run=False
        )
        assert again.applied == 0
        for check_id, check_paths in names.items():
            assert _target_for_id(library["db"], check_id) == str(
                check_paths[current_index[check_id]]
            )


def test_header_with_to_in_other_column_is_not_misread(library, tmp_path):
    from rename import parse_rename_log

    log = tmp_path / "RENAME-LOG.md"
    log.write_text(
        "| Old path | Note to reviewer | New path | SHA-256 |\n|---|---|---|---|\n"
        f"| API/a.pdf | moved | API/b.pdf | {'e' * 64} |\n",
        encoding="utf-8",
    )
    (entry,) = parse_rename_log(log, library_root="/lib")
    assert entry.new_path == "/lib/API/b.pdf"


def test_parse_stops_at_end_of_rename_table(library, tmp_path):
    from rename import parse_rename_log

    log = tmp_path / "RENAME-LOG.md"
    log.write_text(
        "| Old path | New path | SHA-256 |\n|---|---|---|\n\n"
        "## Deleted\n\n| File | Reason | sha |\n|---|---|---|\n| x | y | sha |\n",
        encoding="utf-8",
    )
    assert parse_rename_log(log, library_root="/lib") == []


def test_posix_library_root_resolves_posix_paths(tmp_path):
    from rename import parse_rename_log

    log = write_log(tmp_path / "RENAME-LOG.md", [("API/./a.pdf", "API/b.pdf", "f" * 64)])
    (entry,) = parse_rename_log(log, library_root="/mnt/lib")
    assert entry.old_path == "/mnt/lib/API/a.pdf"
    assert entry.new_path == "/mnt/lib/API/b.pdf"


def test_row_at_new_path_without_sha_gets_specific_error(library, tmp_path):
    from rename import apply_renames

    conn = sqlite3.connect(library["db"])
    conn.execute("ALTER TABLE documents ADD COLUMN sha256 TEXT")
    conn.execute("UPDATE documents SET target_path=? WHERE id=1", (str(library["new"]),))
    conn.commit()
    conn.close()
    with pytest.raises(ValueError, match="no recorded SHA-256"):
        apply_renames(library["db"], _entries(library, tmp_path), dry_run=False)


# --- remap_source_root -------------------------------------------------------


def test_remap_into_nested_root_is_idempotent(library):
    from rename import remap_source_root

    assert remap_source_root(library["db"], "/old/src", "/old/src/raw", dry_run=False) == 2
    assert remap_source_root(library["db"], "/old/src", "/old/src/raw", dry_run=True) == 0
    assert remap_source_root(library["db"], "/old/src", "/old/src/raw", dry_run=False) == 0
    row = _row(library["db"], library["untouched"])
    assert row["file_path"] == "/old/src/raw/API Spec 6A.pdf"
    assert row["source_dir"] == "/old/src/raw"


def test_remap_flatten_out_of_nested_root(library):
    from rename import remap_source_root

    remap_source_root(library["db"], "/old/src", "/old/src/raw", dry_run=False)
    assert remap_source_root(library["db"], "/old/src/raw", "/old/src", dry_run=False) == 2
    row = _row(library["db"], library["untouched"])
    assert row["file_path"] == "/old/src/API Spec 6A.pdf"
    assert row["source_dir"] == "/old/src"


def test_remap_flatten_replay_does_not_strip_repeated_suffix(library):
    from rename import remap_source_root

    conn = sqlite3.connect(library["db"])
    conn.execute(
        "UPDATE documents SET file_path='/lib/raw/raw/1.pdf', source_dir='/lib/raw' "
        "WHERE id=1"
    )
    conn.commit()
    conn.close()

    assert remap_source_root(library["db"], "/lib/raw", "/lib", dry_run=False) == 1
    row = _row(library["db"], library["old"])
    assert row["file_path"] == "/lib/raw/1.pdf"
    assert row["source_dir"] == "/lib"

    assert remap_source_root(library["db"], "/lib/raw", "/lib", dry_run=True) == 0
    assert remap_source_root(library["db"], "/lib/raw", "/lib", dry_run=False) == 0
    row = _row(library["db"], library["old"])
    assert row["file_path"] == "/lib/raw/1.pdf"
    assert row["source_dir"] == "/lib"


def test_remap_collision_rolls_back(library):
    from rename import remap_source_root

    conn = sqlite3.connect(library["db"])
    conn.execute(
        "INSERT INTO documents (file_path, filename) VALUES ('/lib/raw/API Spec 6A.pdf', 'x')"
    )
    conn.commit()
    conn.close()
    before = library["db"].read_bytes()
    with pytest.raises(ValueError, match="collide"):
        remap_source_root(library["db"], "/old/src", "/lib/raw", dry_run=False)
    assert library["db"].read_bytes() == before


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


def test_main_db_override_regenerates_catalog_from_effective_db(library, tmp_path):
    from rename import main

    override_db = tmp_path / "override.db"
    override_db.write_bytes(library["db"].read_bytes())
    write_log(
        library["root"] / "RENAME-LOG.md",
        [("API/API RP 2RD (2013).pdf", "API/API RP 2RD (2013 draft).pdf", library["sha"])],
    )
    rc = main(["--config", str(library["config"]), "--db", str(override_db)])

    assert rc == 0
    assert _row(library["db"], library["old"]) is not None
    assert _row(override_db, library["new"]) is not None
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
