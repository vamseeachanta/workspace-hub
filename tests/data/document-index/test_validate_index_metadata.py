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
    """<13% summary_done True → exit 1."""
    index = tmp_path / "index.jsonl"
    # #2334: 100 records, 95 non-other, 10 summary_done True, 80 file_exists True.
    # 10% summary_done < 13% default → FAIL on summary_done dimension;
    # 80% file_exists > 70% default → adjacent dimension clean, isolates the test.
    _write_index(index, _mix_with_file_exists(
        n_non_other=95, n_other=5, n_summary_true=10, n_file_exists_true=80))
    r = _run(index)
    assert r.returncode == 1
    assert "summary_done" in (r.stdout + r.stderr).lower()


# ─────────────────────── Test 23 ───────────────────────
def test_validator_passes_healthy_index(tmp_path):
    """95% non-other + 80% summary_done + 90% summary_file_exists → exit 0."""
    index = tmp_path / "index.jsonl"
    # #2309: use the file_exists-aware fixture so the new threshold is also met
    _write_index(index, _mix_with_file_exists(
        n_non_other=95, n_other=5, n_summary_true=80, n_file_exists_true=90))
    r = _run(index)
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"


# ─────────────────────── Test 24 ───────────────────────
def test_validator_thresholds_overridable_via_cli(tmp_path):
    """--summary-done-min 0.05 relaxes the default 0.13 threshold."""
    index = tmp_path / "index.jsonl"
    # #2334: 100 records, 95 non-other, 10 summary_done True, 80 summary_file_exists True
    _write_index(index, _mix_with_file_exists(
        n_non_other=95, n_other=5, n_summary_true=10, n_file_exists_true=80))
    # Default 0.13 threshold → FAIL (10% < 13%)
    assert _run(index).returncode == 1
    # Relaxed to 0.05 → PASS (10% > 5%; file_exists 80% > 70% default)
    assert _run(index, "--summary-done-min", "0.05").returncode == 0


def test_validator_empty_index_exits_1(tmp_path):
    """Empty file should not silently pass."""
    index = tmp_path / "index.jsonl"
    index.write_text("")
    assert _run(index).returncode == 1


# ═══════════════ #2309 summary_file_exists threshold tests ═══════════════

def _mix_with_file_exists(n_non_other, n_other, n_summary_true, n_file_exists_true):
    """Like _mix but also sets summary_file_exists on the first n records."""
    records = []
    for _ in range(n_non_other):
        records.append({"path": f"/x{len(records)}.pdf", "content_type": "document",
                        "summary_done": False, "summary_file_exists": False})
    for _ in range(n_other):
        records.append({"path": f"/x{len(records)}.xyz", "content_type": "other",
                        "summary_done": False, "summary_file_exists": False})
    # Flip summary_done True on first N records
    to_flip_done = n_summary_true
    for r in records:
        if to_flip_done <= 0:
            break
        r["summary_done"] = True
        r["summary_file_exists"] = True  # summary_done implies file_exists
        to_flip_done -= 1
    # Flip summary_file_exists=True on additional records (above the summary_done set)
    to_flip_fe = n_file_exists_true - n_summary_true  # already flipped some
    for r in records:
        if to_flip_fe <= 0:
            break
        if r["summary_file_exists"] is False:
            r["summary_file_exists"] = True
            to_flip_fe -= 1
    return records


def test_validator_rejects_low_summary_file_exists(tmp_path):
    """<70% summary_file_exists=True → exit 1 (new threshold, default 0.70)."""
    index = tmp_path / "index.jsonl"
    # 100 records; 95 non-other; 20 summary_done=True; 60 summary_file_exists=True (60% < 70%)
    _write_index(index, _mix_with_file_exists(
        n_non_other=95, n_other=5, n_summary_true=20, n_file_exists_true=60))
    r = _run(index)
    assert r.returncode == 1
    assert "summary_file_exists" in (r.stdout + r.stderr).lower()


def test_validator_summary_file_exists_min_cli_override(tmp_path):
    """--summary-file-exists-min 0.50 relaxes the default 0.70."""
    index = tmp_path / "index.jsonl"
    # 100 records; 95 non-other; 60 summary_done; 60 summary_file_exists=True
    # We use 60 summary_done (above 55% default) so only summary_file_exists threshold is tested.
    _write_index(index, _mix_with_file_exists(
        n_non_other=95, n_other=5, n_summary_true=60, n_file_exists_true=60))
    # Default 0.70 → FAIL (60% < 70%)
    assert _run(index).returncode == 1
    # Relaxed to 0.50 → PASS
    assert _run(index, "--summary-file-exists-min", "0.50").returncode == 0


def test_validator_passes_when_all_three_thresholds_met(tmp_path):
    """Healthy index with all 3 thresholds met → exit 0."""
    index = tmp_path / "index.jsonl"
    # 100 records; 95 non-other; 70 summary_done; 90 summary_file_exists
    _write_index(index, _mix_with_file_exists(
        n_non_other=95, n_other=5, n_summary_true=70, n_file_exists_true=90))
    r = _run(index)
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"


# ═══════════════ #2334 default calibration tests ═══════════════

def test_default_summary_done_min_is_point_one_three(tmp_path):
    """Pin the post-#2334 calibration floor (~3pp below measured 16.13%)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("validator_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ns = mod._parse_args(["--index", str(tmp_path / "ignored.jsonl")])
    assert ns.summary_done_min == 0.13


def test_docstring_summary_done_min_matches_argparse_default():
    """Prevent docstring-argparse drift — pins both sides in lockstep."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("validator_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert "--summary-done-min           0.13" in mod.__doc__, (
        "Docstring threshold value drifted from argparse default. "
        "Both scripts/data/document-index/validate-index-metadata.py:19 and :35 must be updated together."
    )
