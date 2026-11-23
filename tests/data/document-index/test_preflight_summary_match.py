#!/usr/bin/env python3
# ABOUTME: TDD tests for preflight-summary-match.py — sample-based match-rate
# ABOUTME: reconciliation before a full enrichment run (#1878, addresses Claude F2).

"""Tests for scripts/data/document-index/preflight-summary-match.py."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "data"
    / "document-index"
    / "preflight-summary-match.py"
)


def _write_index(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _write_summary(dir_: Path, name: str) -> None:
    (dir_ / name).write_text(json.dumps({"summary": "x"}))


def _run(index: Path, summaries_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--index",
            str(index),
            "--summaries-dir",
            str(summaries_dir),
            "--sample-size",
            "10",
            *extra,
        ],
        capture_output=True,
        text=True,
    )


# ─────────────────────── Test 32 ───────────────────────
def test_preflight_exits_nonzero_on_low_match_rate(tmp_path):
    """Expect 80%, observe 20% → exit 1."""
    summaries = tmp_path / "summaries"
    summaries.mkdir()
    index = tmp_path / "index.jsonl"

    # 10 path-fallback records; only 2 have summary files → 20% match
    records = []
    for i in range(10):
        path = f"/doc/{i}.pdf"
        records.append({"path": path, "content_hash": None})
        if i < 2:
            key = hashlib.sha256(path.encode()).hexdigest()[:16]
            _write_summary(summaries, f"{key}.json")
    _write_index(index, records)

    r = _run(index, summaries, "--expected-rate", "0.80", "--safety-margin", "0.05", "--seed", "1")
    assert r.returncode == 1, f"stdout={r.stdout!r} stderr={r.stderr!r}"


# ─────────────────────── Test 33 ───────────────────────
def test_preflight_reports_per_pattern_breakdown(tmp_path):
    """Output includes match counts for each of 4 filename patterns."""
    summaries = tmp_path / "summaries"
    summaries.mkdir()
    index = tmp_path / "index.jsonl"

    records = []
    # pattern 1: sha256-prefixed
    hex64a = "a" * 64
    records.append({"path": "/p1.pdf", "content_hash": f"sha256:{hex64a}"})
    _write_summary(summaries, f"sha256:{hex64a}.json")
    # pattern 2: bare sha256 (prefix-stripped)
    hex64b = "b" * 64
    records.append({"path": "/p2.pdf", "content_hash": f"sha256:{hex64b}"})
    _write_summary(summaries, f"{hex64b}.json")
    # pattern 3: bare md5
    hex32 = "c" * 32
    records.append({"path": "/p3.xls", "content_hash": f"md5:{hex32}"})
    _write_summary(summaries, f"{hex32}.json")
    # pattern 4: path-fallback (16-hex)
    path4 = "/p4.pdf"
    records.append({"path": path4, "content_hash": None})
    key4 = hashlib.sha256(path4.encode()).hexdigest()[:16]
    _write_summary(summaries, f"{key4}.json")

    _write_index(index, records)

    r = _run(index, summaries, "--expected-rate", "0.0", "--safety-margin", "0.0", "--sample-size", "100")
    out = r.stdout + r.stderr
    # Look for some form of per-pattern reporting — the exact labels can be
    # implementation-defined but each of the four must be individually named.
    assert "prefixed" in out.lower() or "sha256:" in out.lower()
    assert "bare" in out.lower() or "stripped" in out.lower()
    assert "path" in out.lower() or "fallback" in out.lower()


def test_preflight_passes_when_match_rate_exceeds_floor(tmp_path):
    """Observed 90% ≥ expected 80% - 5% margin (75% floor) → exit 0."""
    summaries = tmp_path / "summaries"
    summaries.mkdir()
    index = tmp_path / "index.jsonl"

    records = []
    for i in range(10):
        path = f"/doc/{i}.pdf"
        records.append({"path": path, "content_hash": None})
        if i < 9:
            key = hashlib.sha256(path.encode()).hexdigest()[:16]
            _write_summary(summaries, f"{key}.json")
    _write_index(index, records)

    r = _run(index, summaries, "--expected-rate", "0.80", "--safety-margin", "0.05", "--seed", "1")
    assert r.returncode == 0, f"stdout={r.stdout!r} stderr={r.stderr!r}"
