#!/usr/bin/env python3
# ABOUTME: TDD tests for _carryover_metadata.py — preserves enriched fields
# ABOUTME: across Phase A/C/E rewrites of index.jsonl (#1878, Codex Finding #3).

"""Tests for scripts/data/document-index/_carryover_metadata.py."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)


def _write_index(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _read_index(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ───────────────── extract_enriched_fields ─────────────────
def test_extract_enriched_fields_from_existing_index(tmp_path):
    from _carryover_metadata import extract_enriched_fields

    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {"path": "/a.pdf", "content_type": "document", "summary_done": True},
            {"path": "/b.pdf", "content_type": "other", "summary_done": False},
            {"path": "/c.pdf"},  # unenriched — should be skipped
        ],
    )
    got = extract_enriched_fields(idx)
    assert got == {
        "/a.pdf": {"content_type": "document", "summary_done": True},
        "/b.pdf": {"content_type": "other", "summary_done": False},
    }


def test_extract_enriched_fields_returns_empty_for_missing_file(tmp_path):
    from _carryover_metadata import extract_enriched_fields

    assert extract_enriched_fields(tmp_path / "nothere.jsonl") == {}


# ───────────────── apply_carryover ─────────────────
def test_apply_carryover_merges_fields_by_path():
    from _carryover_metadata import apply_carryover

    side = {
        "/a.pdf": {"content_type": "document", "summary_done": True},
        "/b.pdf": {"content_type": "cad", "summary_done": False},
    }
    new = [
        {"path": "/a.pdf", "ext": "pdf", "domain": "marine"},
        {"path": "/b.pdf", "ext": "dwg"},
        {"path": "/c.pdf", "ext": "pdf"},  # no carryover available
    ]
    out = apply_carryover(new, side)
    by_path = {r["path"]: r for r in out}
    assert by_path["/a.pdf"]["content_type"] == "document"
    assert by_path["/a.pdf"]["summary_done"] is True
    assert by_path["/a.pdf"]["domain"] == "marine"  # prior fields preserved
    assert by_path["/b.pdf"]["content_type"] == "cad"
    assert "content_type" not in by_path["/c.pdf"]  # no carryover → untouched


def test_apply_carryover_does_not_overwrite_newer_values():
    """If the new record already has enriched fields (e.g., from re-enrichment),
    do NOT overwrite with stale side-dict values."""
    from _carryover_metadata import apply_carryover

    side = {"/a.pdf": {"content_type": "document", "summary_done": False}}
    new = [{"path": "/a.pdf", "content_type": "spreadsheet", "summary_done": True}]
    out = apply_carryover(new, side)
    assert out[0]["content_type"] == "spreadsheet"
    assert out[0]["summary_done"] is True


# ───────────────── atomic_write_index ─────────────────
def test_atomic_write_creates_dated_backup(tmp_path):
    from _carryover_metadata import atomic_write_index

    idx = tmp_path / "index.jsonl"
    _write_index(idx, [{"path": "/old.pdf"}])

    atomic_write_index(
        idx,
        [{"path": "/new.pdf", "content_type": "document", "summary_done": False}],
        today="2026-04-16",
    )
    assert (tmp_path / "index.jsonl.backup-2026-04-16").exists()
    out = _read_index(idx)
    assert out == [{"path": "/new.pdf", "content_type": "document", "summary_done": False}]


def test_atomic_write_safe_under_rename_failure(monkeypatch, tmp_path):
    """If os.replace fails, the original index.jsonl is untouched."""
    from _carryover_metadata import atomic_write_index

    idx = tmp_path / "index.jsonl"
    _write_index(idx, [{"path": "/old.pdf", "marker": "PRIOR"}])
    original_bytes = idx.read_bytes()

    def boom(*a, **k):
        raise OSError("simulated")

    monkeypatch.setattr(os, "replace", boom)
    monkeypatch.setattr(os, "rename", boom)

    with pytest.raises(OSError):
        atomic_write_index(
            idx,
            [{"path": "/new.pdf"}],
            today="2026-04-16",
        )

    # Original index.jsonl untouched
    assert idx.read_bytes() == original_bytes


def test_atomic_write_does_not_overwrite_existing_backup(tmp_path):
    """Second run on same day should not clobber the backup."""
    from _carryover_metadata import atomic_write_index

    idx = tmp_path / "index.jsonl"
    _write_index(idx, [{"path": "/first.pdf"}])

    atomic_write_index(idx, [{"path": "/second.pdf"}], today="2026-04-16")
    first_backup = (tmp_path / "index.jsonl.backup-2026-04-16").read_bytes()

    # Second invocation same day — the pre-existing backup must be preserved
    atomic_write_index(idx, [{"path": "/third.pdf"}], today="2026-04-16")
    assert (tmp_path / "index.jsonl.backup-2026-04-16").read_bytes() == first_backup


# ───────────────── end-to-end with Phase A writeback shape ─────────────────
def test_carryover_end_to_end(tmp_path):
    """Simulate Phase A --force rewrite scenario: enriched index → regenerated →
    merged with carryover → atomic write → enriched fields survive."""
    from _carryover_metadata import (
        apply_carryover,
        atomic_write_index,
        extract_enriched_fields,
    )

    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {"path": "/a.pdf", "ext": "pdf", "content_type": "document", "summary_done": True},
            {"path": "/b.pdf", "ext": "pdf", "content_type": "document", "summary_done": False},
        ],
    )

    # Simulate Phase A rebuild: fresh records without enriched fields
    new_records = [
        {"path": "/a.pdf", "ext": "pdf", "domain": "marine"},
        {"path": "/b.pdf", "ext": "pdf", "domain": "pipeline"},
        {"path": "/c.pdf", "ext": "pdf"},  # brand new
    ]

    side = extract_enriched_fields(idx)
    merged = apply_carryover(new_records, side)
    atomic_write_index(idx, merged, today="2026-04-16")

    out = _read_index(idx)
    by_path = {r["path"]: r for r in out}
    assert by_path["/a.pdf"]["content_type"] == "document"
    assert by_path["/a.pdf"]["summary_done"] is True
    assert by_path["/a.pdf"]["domain"] == "marine"
    assert by_path["/b.pdf"]["summary_done"] is False
    assert "content_type" not in by_path["/c.pdf"]
