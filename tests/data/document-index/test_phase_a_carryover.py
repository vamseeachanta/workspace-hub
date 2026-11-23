#!/usr/bin/env python3
# ABOUTME: TDD tests for phase-a-index.py carryover integration (#1878).
# ABOUTME: Phase A --force must not clobber content_type / summary_done.

"""Tests for Phase A's carryover-aware write path."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)


def _load_phase_a():
    return importlib.import_module("phase-a-index")


def _write_index(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _read_index(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ─────────────────────── Test 25 ───────────────────────
def test_phase_a_preserves_enriched_fields_on_reindex(tmp_path):
    """After --force reindex with preserve_metadata=True, content_type/summary_done survive."""
    mod = _load_phase_a()
    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {"path": "/a.pdf", "ext": "pdf", "content_type": "document", "summary_done": True},
            {"path": "/b.pdf", "ext": "pdf", "content_type": "document", "summary_done": False},
        ],
    )
    # Simulate Phase A rebuild producing fresh records with no enriched fields
    new_records = {
        "/a.pdf": {"path": "/a.pdf", "ext": "pdf", "domain": "marine"},
        "/b.pdf": {"path": "/b.pdf", "ext": "pdf", "domain": "pipeline"},
    }
    mod.write_merged_index_with_carryover(
        index_path=idx,
        merged_index=new_records,
        preserve_metadata=True,
        today="2026-04-16",
    )
    out = _read_index(idx)
    by_path = {r["path"]: r for r in out}
    assert by_path["/a.pdf"]["content_type"] == "document"
    assert by_path["/a.pdf"]["summary_done"] is True
    assert by_path["/a.pdf"]["domain"] == "marine"
    assert by_path["/b.pdf"]["summary_done"] is False


# ─────────────────────── Test 26 ───────────────────────
def test_phase_a_no_preserve_metadata_flag(tmp_path):
    """preserve_metadata=False writes merged index without carryover."""
    mod = _load_phase_a()
    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [{"path": "/a.pdf", "ext": "pdf", "content_type": "document", "summary_done": True}],
    )
    new_records = {"/a.pdf": {"path": "/a.pdf", "ext": "pdf"}}
    mod.write_merged_index_with_carryover(
        index_path=idx,
        merged_index=new_records,
        preserve_metadata=False,
        today="2026-04-16",
    )
    out = _read_index(idx)
    assert "content_type" not in out[0]
    assert "summary_done" not in out[0]


# ─────────────────────── Test 27 ───────────────────────
def test_phase_a_writes_atomic_with_backup(tmp_path):
    """Dated backup appears after write."""
    mod = _load_phase_a()
    idx = tmp_path / "index.jsonl"
    _write_index(idx, [{"path": "/x.pdf"}])
    mod.write_merged_index_with_carryover(
        index_path=idx,
        merged_index={"/y.pdf": {"path": "/y.pdf"}},
        preserve_metadata=True,
        today="2026-04-16",
    )
    assert (tmp_path / "index.jsonl.backup-2026-04-16").exists()


# ─────────────────────── Test 28 ───────────────────────
def test_phase_a_content_hash_churn(tmp_path):
    """If content_hash changes between runs, carryover still preserves fields
    because it keys on `path` (not hash)."""
    mod = _load_phase_a()
    idx = tmp_path / "index.jsonl"
    _write_index(
        idx,
        [
            {
                "path": "/churner.pdf",
                "content_hash": "sha256:" + "0" * 64,
                "content_type": "document",
                "summary_done": True,
            }
        ],
    )
    new_records = {
        "/churner.pdf": {
            "path": "/churner.pdf",
            "content_hash": "sha256:" + "f" * 64,  # changed content hash
        }
    }
    mod.write_merged_index_with_carryover(
        index_path=idx,
        merged_index=new_records,
        preserve_metadata=True,
        today="2026-04-16",
    )
    out = _read_index(idx)
    assert out[0]["content_type"] == "document"
    assert out[0]["summary_done"] is True
    assert out[0]["content_hash"] == "sha256:" + "f" * 64  # new hash written
