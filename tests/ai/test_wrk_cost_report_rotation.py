"""Tests that wrk_cost_report.py reads rotated `.jsonl.gz` archives — #2070.

Run:
    uv run --no-project python -m pytest tests/ai/test_wrk_cost_report_rotation.py -v
"""

import gzip
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "ai"))

import wrk_cost_report  # noqa: E402


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _write_gz_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _rec(wrk: str, cost: float = 0.01) -> dict:
    return {"wrk": wrk, "input_tokens": 1, "output_tokens": 1,
            "cost_usd": cost, "provider": "claude"}


def test_loads_live_only_when_no_archive(tmp_path):
    """Backward compat: no archive/ subdir, just the live file."""
    live = tmp_path / "cost-tracking.jsonl"
    _write_jsonl(live, [_rec("WRK-LIVE")])
    records, skipped = wrk_cost_report.load_records(live)
    assert [r["wrk"] for r in records] == ["WRK-LIVE"]
    assert skipped == 0


def test_loads_live_plus_gz_archive(tmp_path):
    """Pre-implementation gate: rotated history must be readable alongside live."""
    live = tmp_path / "cost-tracking.jsonl"
    _write_jsonl(live, [_rec("WRK-LIVE")])
    _write_gz_jsonl(tmp_path / "archive" / "cost-tracking-2026-04-01.jsonl.gz",
                    [_rec("WRK-A"), _rec("WRK-B")])
    records, skipped = wrk_cost_report.load_records(live)
    wrks = sorted(r["wrk"] for r in records)
    assert wrks == ["WRK-A", "WRK-B", "WRK-LIVE"]
    assert skipped == 0


def test_loads_only_archives_when_live_missing(tmp_path):
    """Just-after-rotation: live file may not exist yet, archives still readable."""
    live = tmp_path / "cost-tracking.jsonl"  # not created
    _write_gz_jsonl(tmp_path / "archive" / "cost-tracking-2026-04-01.jsonl.gz",
                    [_rec("WRK-OLD")])
    records, skipped = wrk_cost_report.load_records(live)
    assert [r["wrk"] for r in records] == ["WRK-OLD"]


def test_skips_malformed_lines_in_gz(tmp_path):
    """Malformed lines in the gz archive must be skipped, not crash."""
    live = tmp_path / "cost-tracking.jsonl"
    _write_jsonl(live, [_rec("WRK-OK")])
    arc = tmp_path / "archive" / "cost-tracking-2026-03-01.jsonl.gz"
    arc.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(arc, "wt", encoding="utf-8") as f:
        f.write(json.dumps(_rec("WRK-VALID")) + "\n")
        f.write("not json at all\n")
        f.write(json.dumps(_rec("WRK-VALID2")) + "\n")
    records, skipped = wrk_cost_report.load_records(live)
    wrks = sorted(r["wrk"] for r in records)
    assert wrks == ["WRK-OK", "WRK-VALID", "WRK-VALID2"]
    assert skipped == 1


def test_archive_glob_matches_only_dated(tmp_path):
    """Glob is `<stem>-*.jsonl.gz` — unrelated `.gz` files in archive/ are ignored."""
    live = tmp_path / "cost-tracking.jsonl"
    _write_jsonl(live, [_rec("WRK-LIVE")])
    _write_gz_jsonl(tmp_path / "archive" / "cost-tracking-2026-04-01.jsonl.gz",
                    [_rec("WRK-MATCH")])
    _write_gz_jsonl(tmp_path / "archive" / "unrelated.jsonl.gz",
                    [_rec("WRK-IGNORE")])
    records, _ = wrk_cost_report.load_records(live)
    wrks = sorted(r["wrk"] for r in records)
    assert "WRK-MATCH" in wrks
    assert "WRK-IGNORE" not in wrks
