#!/usr/bin/env python3
# ABOUTME: TDD tests for validate-index-metadata.py — regression guard for #1878.
# ABOUTME: Exit 1 if content_type/summary_done coverage drops below thresholds.

"""Tests for scripts/data/document-index/validate-index-metadata.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "data"
    / "document-index"
    / "validate-index-metadata.py"
)


def _write_index(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _run(index_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--index", str(index_path), *extra_args],
        capture_output=True,
        text=True,
    )


def _mix(n_non_other: int, n_other: int, n_missing: int, n_summary_true: int, n_summary_false: int) -> list[dict]:
    """Synthesize records with controlled field coverage."""
    records: list[dict] = []
    for _ in range(n_non_other):
        records.append({"path": f"/x{len(records)}.pdf", "content_type": "document", "summary_done": False})
    for _ in range(n_other):
        records.append({"path": f"/x{len(records)}.xyz", "content_type": "other", "summary_done": False})
    for _ in range(n_missing):
        records.append({"path": f"/x{len(records)}.zzz"})  # no content_type / summary_done fields
    # Now flip summary_done on the first n_summary_true records that have a content_type
    to_flip = n_summary_true
    for r in records:
        if to_flip <= 0:
            break
        if "content_type" in r:
            r["summary_done"] = True
            to_flip -= 1
    # Append pure summary_false filler if requested
    for _ in range(n_summary_false):
        records.append({"path": f"/x{len(records)}.pdf", "content_type": "document", "summary_done": False})
    return records


# ─────────────────────── Test 20 ───────────────────────
def test_validator_rejects_low_content_type_coverage(tmp_path):
    """<90% non-other content_type → exit 1."""
    # 80 non-other + 20 other = 80% non-other → FAIL
    index = tmp_path / "index.jsonl"
    _write_index(index, _mix(n_non_other=80, n_other=20, n_missing=0, n_summary_true=60, n_summary_false=0))
    r = _run(index)
    assert r.returncode == 1
    assert "content_type" in (r.stdout + r.stderr).lower()


# ─────────────────────── Test 21 ───────────────────────
def test_validator_rejects_missing_content_type_field(tmp_path):
    """>10% records missing content_type field → exit 1."""
    index = tmp_path / "index.jsonl"
    # 80 healthy + 20 missing = 20% missing → FAIL
    _write_index(index, _mix(n_non_other=80, n_other=0, n_missing=20, n_summary_true=60, n_summary_false=0))
    r = _run(index)
    assert r.returncode == 1
    assert "missing" in (r.stdout + r.stderr).lower() or "absent" in (r.stdout + r.stderr).lower()


# ─────────────────────── Test 22 ───────────────────────
def test_validator_rejects_low_summary_done(tmp_path):
    """<55% summary_done True → exit 1."""
    index = tmp_path / "index.jsonl"
    # 100 records, 95 non-other, 50 summary_done True = 50% → FAIL
    _write_index(index, _mix(n_non_other=95, n_other=5, n_missing=0, n_summary_true=50, n_summary_false=0))
    r = _run(index)
    assert r.returncode == 1
    assert "summary_done" in (r.stdout + r.stderr).lower()


# ─────────────────────── Test 23 ───────────────────────
def test_validator_passes_healthy_index(tmp_path):
    """95% non-other + 80% summary_done + 0% missing → exit 0."""
    index = tmp_path / "index.jsonl"
    _write_index(index, _mix(n_non_other=95, n_other=5, n_missing=0, n_summary_true=80, n_summary_false=0))
    r = _run(index)
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"


# ─────────────────────── Test 24 ───────────────────────
def test_validator_thresholds_overridable_via_cli(tmp_path):
    """--summary-done-min 0.40 relaxes the default 0.55 threshold."""
    index = tmp_path / "index.jsonl"
    # 100 records, 95 non-other, 50 summary_done True = 50%
    _write_index(index, _mix(n_non_other=95, n_other=5, n_missing=0, n_summary_true=50, n_summary_false=0))
    # Default 0.55 threshold → FAIL
    assert _run(index).returncode == 1
    # Relaxed to 0.40 → PASS
    assert _run(index, "--summary-done-min", "0.40").returncode == 0


def test_validator_empty_index_exits_1(tmp_path):
    """Empty file should not silently pass."""
    index = tmp_path / "index.jsonl"
    index.write_text("")
    assert _run(index).returncode == 1
