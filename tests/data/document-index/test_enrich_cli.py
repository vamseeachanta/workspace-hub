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
