#!/usr/bin/env python3
# ABOUTME: TDD tests for enrich-summary-metadata.py CLI orchestration (#1878).
# ABOUTME: Covers dated backup, atomic rename, --resume, all-fields-preserved.

"""Tests for CLI orchestration layer of enrich-summary-metadata.py."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)


def _load():
    return importlib.import_module("enrich-summary-metadata")


@pytest.fixture
def scratch(tmp_path: Path):
    """Isolated index + summaries dir pair."""
    summaries = tmp_path / "summaries"
    summaries.mkdir()
    index = tmp_path / "index.jsonl"
    return {
        "dir": tmp_path,
        "summaries": summaries,
        "index": index,
    }


def _write_index(index_path: Path, records: list[dict]) -> None:
    with open(index_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _read_index(index_path: Path) -> list[dict]:
    with open(index_path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ───────────────────────────── Test 16 ─────────────────────────────
def test_enrichment_writes_dated_backup_before_overwrite(scratch):
    """After enrich_index() completes, index.jsonl.backup-YYYY-MM-DD exists."""
    mod = _load()
    _write_index(scratch["index"], [{"path": "/a.pdf", "ext": "pdf", "content_hash": None}])

    mod.enrich_index(
        index_path=scratch["index"],
        summaries_dir=scratch["summaries"],
        workers=1,
        resume=False,
        dry_run=False,
        today="2026-04-16",
    )
    assert (scratch["dir"] / "index.jsonl.backup-2026-04-16").exists()


# ───────────────────────────── Test 17 ─────────────────────────────
def test_enrichment_atomic_rename_via_monkeypatched_os_rename(monkeypatch, scratch):
    """If os.rename raises mid-run, the original index.jsonl is untouched."""
    mod = _load()
    original_records = [{"path": "/a.pdf", "ext": "pdf", "content_hash": None, "marker": "orig"}]
    _write_index(scratch["index"], original_records)
    original_bytes = scratch["index"].read_bytes()

    import os as _os

    def boom(*args, **kwargs):
        raise OSError("simulated rename failure")

    monkeypatch.setattr(_os, "replace", boom)
    monkeypatch.setattr(_os, "rename", boom)

    with pytest.raises(OSError):
        mod.enrich_index(
            index_path=scratch["index"],
            summaries_dir=scratch["summaries"],
            workers=1,
            resume=False,
            dry_run=False,
            today="2026-04-16",
        )

    # Original file untouched — content identical
    assert scratch["index"].read_bytes() == original_bytes


# ───────────────────────────── Test 18 ─────────────────────────────
def test_enrichment_resume_skips_already_enriched_records(scratch):
    """With --resume, records that already have both fields are passed through unchanged."""
    mod = _load()
    already = {
        "path": "/a.pdf",
        "ext": "pdf",
        "content_hash": None,
        "content_type": "MARKED",  # sentinel — should NOT be overwritten under --resume
        "summary_done": True,
        "summary_file_exists": True,  # #2309: resume now requires all 3 fields present
    }
    fresh = {"path": "/b.pdf", "ext": "pdf", "content_hash": None}
    _write_index(scratch["index"], [already, fresh])

    mod.enrich_index(
        index_path=scratch["index"],
        summaries_dir=scratch["summaries"],
        workers=1,
        resume=True,
        dry_run=False,
        today="2026-04-16",
    )

    out = _read_index(scratch["index"])
    by_path = {r["path"]: r for r in out}
    assert by_path["/a.pdf"]["content_type"] == "MARKED"  # preserved
    assert by_path["/b.pdf"]["content_type"] == "document"  # freshly enriched
    assert by_path["/b.pdf"]["summary_done"] is False


# ───────────────────────────── Test 19 ─────────────────────────────
def test_enrichment_preserves_all_prior_fields(scratch):
    """No prior field is deleted, renamed, or mutated by enrichment."""
    mod = _load()
    record = {
        "path": "/deep.pdf",
        "host": "ace-linux-1",
        "source": "og_standards",
        "ext": "pdf",
        "size_mb": 1.23,
        "mtime": "2020-01-01T00:00:00",
        "content_hash": None,
        "domain": "marine",
        "summary": None,
        "org": "DNV",
        "status": "done",
        "target_repos": ["x", "y"],
        "readability": "machine",
        "path_category": "standards",
        "path_subcategory": "general-standards",
        "provenance": [{"source": "og_standards"}],
    }
    _write_index(scratch["index"], [record])

    mod.enrich_index(
        index_path=scratch["index"],
        summaries_dir=scratch["summaries"],
        workers=1,
        resume=False,
        dry_run=False,
        today="2026-04-16",
    )

    out = _read_index(scratch["index"])
    assert len(out) == 1
    got = out[0]
    # All original keys and values preserved
    for k, v in record.items():
        assert got[k] == v, f"field {k} changed: {record[k]!r} → {got[k]!r}"
    # Two new keys added
    assert got["content_type"] == "document"
    assert got["summary_done"] is False


# ───────────────────────── Dry-run does not modify file ───────────────────────
def test_dry_run_does_not_write_or_backup(scratch):
    mod = _load()
    _write_index(scratch["index"], [{"path": "/a.pdf", "ext": "pdf", "content_hash": None}])
    original_bytes = scratch["index"].read_bytes()

    stats = mod.enrich_index(
        index_path=scratch["index"],
        summaries_dir=scratch["summaries"],
        workers=1,
        resume=False,
        dry_run=True,
        today="2026-04-16",
    )
    assert scratch["index"].read_bytes() == original_bytes
    assert not (scratch["dir"] / "index.jsonl.backup-2026-04-16").exists()
    # Stats returned so the caller can print a coverage report
    assert stats["total"] == 1
    assert stats["content_type_non_other"] == 1
    assert stats["summary_done_true"] == 0
    # #2309: stats dict now includes summary_file_exists counter
    assert stats["summary_file_exists_true"] == 0


# ═══════════════════════ #2309 resume + stats coverage ═══════════════════════

def test_enrich_index_stats_includes_summary_file_exists_true(scratch):
    """Dry-run stats dict exposes summary_file_exists_true counter (#2309 test 6)."""
    mod = _load()
    import hashlib

    # Record A: summary file exists with non-empty content
    path_a = "/a.pdf"
    key_a = hashlib.sha256(path_a.encode()).hexdigest()[:16]
    (scratch["summaries"] / f"{key_a}.json").write_text(
        json.dumps({"summary": "real"}), encoding="utf-8"
    )
    # Record B: summary file exists but empty content
    path_b = "/b.pdf"
    key_b = hashlib.sha256(path_b.encode()).hexdigest()[:16]
    (scratch["summaries"] / f"{key_b}.json").write_text(
        json.dumps({"summary": ""}), encoding="utf-8"
    )
    # Record C: no summary file
    path_c = "/c.pdf"

    _write_index(
        scratch["index"],
        [
            {"path": path_a, "ext": "pdf", "content_hash": None},
            {"path": path_b, "ext": "pdf", "content_hash": None},
            {"path": path_c, "ext": "pdf", "content_hash": None},
        ],
    )

    stats = mod.enrich_index(
        index_path=scratch["index"],
        summaries_dir=scratch["summaries"],
        workers=1,
        resume=False,
        dry_run=True,
        today="2026-04-17",
    )
    assert stats["total"] == 3
    assert stats["summary_file_exists_true"] == 2  # A + B
    assert stats["summary_done_true"] == 1  # only A has non-empty content


def test_resume_re_enriches_pre_split_records(scratch):
    """--resume MUST NOT skip pre-#2309 records that have content_type + summary_done
    but lack summary_file_exists. Otherwise the split never applies. (Claude F1, Codex F1)"""
    mod = _load()

    # Pre-split record: has the two #1878 fields but not summary_file_exists
    pre_split = {
        "path": "/pre.pdf",
        "ext": "pdf",
        "content_hash": None,
        "content_type": "document",
        "summary_done": False,
        # summary_file_exists intentionally absent
    }
    _write_index(scratch["index"], [pre_split])

    mod.enrich_index(
        index_path=scratch["index"],
        summaries_dir=scratch["summaries"],
        workers=1,
        resume=True,
        dry_run=False,
        today="2026-04-17",
    )

    out = _read_index(scratch["index"])
    assert len(out) == 1
    # summary_file_exists MUST now be present (record was NOT skipped)
    assert "summary_file_exists" in out[0]
    assert out[0]["summary_file_exists"] is False  # no file on disk
