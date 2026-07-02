"""Tests for #3340: drive-index-search invocation metrics + weekly aggregate.

Covers metrics.py emission (schema, hashing/privacy, opt-out, session-id
resolution, fail-open), the end-to-end CLI emission point in search.py, the
nudge-hook JSONL append (#3339 coordinated addition), aggregate_metrics.py
(counts/rates, nudge-conversion join, nudges_log_absent, malformed tolerance,
privacy pin, idempotency), and the gitignore residency split.

Run: python3 -m pytest tests/data/drive_index_search/test_metrics_3340.py -v
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

import pytest

import aggregate_metrics as agg_mod
import metrics as metrics_mod

REPO_ROOT = Path(__file__).resolve().parents[3]
CLI = REPO_ROOT / "scripts" / "data" / "drive-index-search" / "search.py"
NUDGE_HOOK = REPO_ROOT / ".claude" / "hooks" / "drive-file-nudge.sh"
NUDGE_MAP = REPO_ROOT / ".claude" / "hooks" / "drive-file-map.json"

# Fixed test week: 2026-W20 (Wednesday of that week), well away from "now".
WEEK = "2026-W20"
TS_IN_WEEK = "2026-05-13T12:00:00+00:00"

EXPECTED_KEYS = {
    "ts", "session", "caller", "query_hash", "n_tokens", "n_results",
    "top_score", "json_flag", "indexes_queried", "coverage_gaps",
    "n_stale_indexes", "exit_code", "duration_ms",
}


def _args(**overrides):
    base = dict(query="mooring fatigue", caller="skill", as_json=True, session=None)
    base.update(overrides)
    return Namespace(**base)


def _envelope(n_results=2, top=0.8, gaps=0, index_status=None):
    envelope = {
        "query": "mooring fatigue",
        "generated_at": TS_IN_WEEK,
        "indexes_queried": ["fixture_a", "fixture_b"],
        "coverage_gaps": [{"id": f"gap{i}", "reason": "unreachable"} for i in range(gaps)],
        "results": [
            {"canonical_path": f"/fixture/ace/file{i}.xlsx", "score": round(top - 0.1 * i, 3)}
            for i in range(n_results)
        ],
    }
    if index_status is not None:
        envelope["index_status"] = index_status
    return envelope


@pytest.fixture()
def metrics_dir(tmp_path, monkeypatch):
    target = tmp_path / "metrics"
    monkeypatch.setenv("DRIVE_SEARCH_METRICS_DIR", str(target))
    monkeypatch.delenv("DRIVE_SEARCH_NO_METRICS", raising=False)
    monkeypatch.delenv("DRIVE_SEARCH_LOG_RAW_QUERY", raising=False)
    return target


def _emitted_lines(metrics_dir: Path) -> list[dict]:
    log = metrics_dir / "invocations.jsonl"
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text().splitlines() if line.strip()]


# ── emission: schema + privacy ────────────────────────────────────────────


def test_emit_writes_schema_line(metrics_dir):
    metrics_mod.emit_invocation(_args(), _envelope(), 0, time.monotonic())

    lines = _emitted_lines(metrics_dir)
    assert len(lines) == 1
    line = lines[0]
    assert set(line) == EXPECTED_KEYS
    assert len(line["query_hash"]) == 12
    int(line["query_hash"], 16)  # 12-hex
    assert line["n_tokens"] == 2
    assert line["caller"] == "skill"
    assert isinstance(line["top_score"], float)
    assert line["n_results"] == 2
    assert line["indexes_queried"] == 2
    assert line["json_flag"] is True
    assert line["n_stale_indexes"] == 0  # index_status absent -> 0 (r1 F2)
    assert line["exit_code"] == 0
    assert isinstance(line["duration_ms"], int)


def test_emit_hashes_never_raw_query(metrics_dir):
    query = "clientCo-proj42 mooring layout"
    metrics_mod.emit_invocation(_args(query=query), _envelope(), 0, time.monotonic())

    raw = (metrics_dir / "invocations.jsonl").read_bytes()
    assert b"clientCo-proj42" not in raw
    expected = hashlib.sha256(query.encode()).hexdigest()[:12]
    assert expected.encode() in raw


def test_emit_raw_query_optin(metrics_dir, monkeypatch):
    monkeypatch.setenv("DRIVE_SEARCH_LOG_RAW_QUERY", "1")
    query = "clientCo-proj42 mooring layout"
    metrics_mod.emit_invocation(_args(query=query), _envelope(), 0, time.monotonic())

    line = _emitted_lines(metrics_dir)[0]
    assert line["query_raw"] == query


def test_emit_stale_index_count(metrics_dir):
    status = [{"id": "a", "stale": True}, {"id": "b", "stale": False}, {"id": "c", "stale": True}]
    metrics_mod.emit_invocation(_args(), _envelope(index_status=status), 0, time.monotonic())

    assert _emitted_lines(metrics_dir)[0]["n_stale_indexes"] == 2


def test_emit_empty_results(metrics_dir):
    metrics_mod.emit_invocation(_args(), _envelope(n_results=0), 0, time.monotonic())

    line = _emitted_lines(metrics_dir)[0]
    assert line["n_results"] == 0
    assert line["top_score"] is None


# ── emission: session precedence, opt-out, fail-open ─────────────────────


def test_emit_session_precedence(metrics_dir, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "env-session")
    metrics_mod.emit_invocation(_args(session="flag-session"), _envelope(), 0, time.monotonic())
    metrics_mod.emit_invocation(_args(session=None), _envelope(), 0, time.monotonic())
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID")
    metrics_mod.emit_invocation(_args(session=None), _envelope(), 0, time.monotonic())

    sessions = [line["session"] for line in _emitted_lines(metrics_dir)]
    assert sessions == ["flag-session", "env-session", "unknown"]


def test_emit_disabled_by_env(metrics_dir, monkeypatch):
    monkeypatch.setenv("DRIVE_SEARCH_NO_METRICS", "1")
    metrics_mod.emit_invocation(_args(), _envelope(), 0, time.monotonic())

    assert not (metrics_dir / "invocations.jsonl").exists()


@pytest.mark.skipif(os.geteuid() == 0, reason="chmod 0 does not stop root")
def test_emit_fail_open(tmp_path, monkeypatch):
    blocked = tmp_path / "blocked"
    blocked.mkdir()
    blocked.chmod(0)
    monkeypatch.setenv("DRIVE_SEARCH_METRICS_DIR", str(blocked / "metrics"))
    try:
        metrics_mod.emit_invocation(_args(), _envelope(), 0, time.monotonic())  # must not raise
    finally:
        blocked.chmod(0o700)


# ── end-to-end: the search.py emission point ──────────────────────────────


def _run_cli(args, extra_env):
    env = dict(os.environ)
    env.pop("DRIVE_SEARCH_NO_METRICS", None)
    env.pop("DRIVE_SEARCH_LOG_RAW_QUERY", None)
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=REPO_ROOT, env=env, text=True, capture_output=True, check=False,
    )


def test_cli_fixture_run_emits_line(fixture_registry, tmp_path):
    target = tmp_path / "metrics"
    args = ["riser", "--registry", str(fixture_registry), "--json",
            "--caller", "pre-calc", "--session", "t1"]

    with_metrics = _run_cli(args, {"DRIVE_SEARCH_METRICS_DIR": str(target)})
    without = _run_cli(args, {"DRIVE_SEARCH_METRICS_DIR": str(target),
                              "DRIVE_SEARCH_NO_METRICS": "1"})

    assert with_metrics.returncode == 0
    # stdout envelope unchanged by metrics (modulo the generated_at timestamp)
    payload_a = json.loads(with_metrics.stdout)
    payload_b = json.loads(without.stdout)
    payload_a.pop("generated_at"), payload_b.pop("generated_at")
    assert payload_a == payload_b

    lines = _emitted_lines(target)
    assert len(lines) == 1  # the NO_METRICS run added nothing
    assert lines[0]["caller"] == "pre-calc"
    assert lines[0]["session"] == "t1"
    assert set(lines[0]) == EXPECTED_KEYS


# ── nudge hook: the #3339 coordinated JSONL append ────────────────────────


def test_nudge_hook_appends_metrics_line(tmp_path):
    if shutil.which("jq") is None:
        pytest.skip("jq not installed")
    hooks = tmp_path / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy(NUDGE_HOOK, hooks / "drive-file-nudge.sh")
    shutil.copy(NUDGE_MAP, hooks / "drive-file-map.json")
    env = dict(os.environ)
    env["WORKSPACE_HUB"] = str(tmp_path)
    env["DRIVE_NUDGE_STATE_DIR"] = str(tmp_path)
    payload = json.dumps(
        {"prompt": "set up a fatigue analysis like we did before", "session_id": "nudge-t1"}
    )

    proc = subprocess.run(
        ["bash", str(hooks / "drive-file-nudge.sh")],
        input=payload, env=env, capture_output=True, text=True, timeout=15,
    )

    assert proc.returncode == 0
    assert "[drive-file]" in proc.stdout
    nudge_log = tmp_path / "data" / "drive-index-search" / "metrics" / "nudges.jsonl"
    assert nudge_log.exists()
    lines = [json.loads(line) for line in nudge_log.read_text().splitlines()]
    assert len(lines) == 1
    assert lines[0]["session"] == "nudge-t1"
    assert set(lines[0]) == {"ts", "session"}


# ── aggregate: counts, joins, robustness, privacy, idempotency ────────────


def _write_invocations(metrics_dir: Path, rows: list[dict]):
    metrics_dir.mkdir(parents=True, exist_ok=True)
    defaults = dict(
        ts=TS_IN_WEEK, session="s1", caller="manual", query_hash="ab" * 6,
        n_tokens=2, n_results=1, top_score=0.5, json_flag=True,
        indexes_queried=2, coverage_gaps=0, n_stale_indexes=0,
        exit_code=0, duration_ms=100,
    )
    with open(metrics_dir / "invocations.jsonl", "w") as handle:
        for row in rows:
            handle.write(json.dumps({**defaults, **row}) + "\n")


def _write_nudges(metrics_dir: Path, sessions: list[str]):
    metrics_dir.mkdir(parents=True, exist_ok=True)
    with open(metrics_dir / "nudges.jsonl", "w") as handle:
        for session in sessions:
            handle.write(json.dumps({"ts": TS_IN_WEEK, "session": session}) + "\n")


def test_aggregate_counts_and_rates(tmp_path):
    rows = (
        [{"n_results": 3, "top_score": 0.7, "caller": "skill"}] * 4
        + [{"n_results": 1, "top_score": 0.5, "caller": "pre-calc"}] * 2
        + [{"n_results": 0, "top_score": None, "coverage_gaps": 2}] * 3
        + [{"n_results": 2, "top_score": 0.1, "coverage_gaps": 1, "n_stale_indexes": 1}]
    )
    _write_invocations(tmp_path, rows)

    agg = agg_mod.build_aggregate(tmp_path, WEEK, REPO_ROOT)

    assert agg["invocations"] == 10
    assert agg["hit_rate"] == 0.6  # 6 with n_results>=1 and top_score>=HIT_SCORE_MIN
    assert agg["empty_rate"] == 0.3
    assert agg["gap_rate"] == 0.4
    assert agg["stale_rate"] == 0.1
    assert agg["by_caller"] == {"skill": 4, "pre-calc": 2, "manual": 4}
    assert agg["median_duration_ms"] == 100
    assert agg["week"] == WEEK
    assert agg["host"] == socket.gethostname()


def test_aggregate_nudge_conversion(tmp_path):
    _write_invocations(
        tmp_path,
        [{"session": "b"}, {"session": "c"}, {"session": "d"}, {"session": "unknown"}],
    )
    _write_nudges(tmp_path, ["a", "b", "c", "unknown"])  # unknown excluded from join

    agg = agg_mod.build_aggregate(tmp_path, WEEK, REPO_ROOT)

    assert agg["nudge_firings"] == 4
    assert agg["nudge_conversion"] == round(2 / 3, 4)
    assert agg["nudges_log_absent"] is False


def test_aggregate_zero_nudges(tmp_path):
    _write_invocations(tmp_path, [{}])
    (tmp_path / "nudges.jsonl").write_text("")

    agg = agg_mod.build_aggregate(tmp_path, WEEK, REPO_ROOT)

    assert agg["nudge_firings"] == 0
    assert agg["nudge_conversion"] is None
    assert agg["nudges_log_absent"] is False


def test_aggregate_nudges_log_absent_distinct(tmp_path):
    _write_invocations(tmp_path, [{}])

    agg = agg_mod.build_aggregate(tmp_path, WEEK, REPO_ROOT)

    assert agg["nudges_log_absent"] is True  # absent reported DISTINCTLY from 0 (r1 F5)
    assert agg["nudge_firings"] == 0
    assert agg["nudge_conversion"] is None


def test_aggregate_skips_malformed(tmp_path):
    _write_invocations(tmp_path, [{}, {}])
    with open(tmp_path / "invocations.jsonl", "a") as handle:
        handle.write("{not json\n")
    _write_nudges(tmp_path, ["a"])
    with open(tmp_path / "nudges.jsonl", "a") as handle:
        handle.write("garbage line\n")

    agg = agg_mod.build_aggregate(tmp_path, WEEK, REPO_ROOT)

    assert agg["malformed_lines"] == 2
    assert agg["invocations"] == 2
    assert agg["nudge_firings"] == 1


def test_aggregate_out_of_week_lines_excluded(tmp_path):
    _write_invocations(tmp_path, [{}, {"ts": "2026-06-01T00:00:00+00:00"}])

    agg = agg_mod.build_aggregate(tmp_path, WEEK, REPO_ROOT)

    assert agg["invocations"] == 1


def _run_aggregate_cli(metrics_dir: Path) -> Path:
    rc = agg_mod.main(["--week", WEEK, "--metrics-dir", str(metrics_dir),
                       "--repo-root", str(REPO_ROOT)])
    assert rc == 0
    return metrics_dir / "weekly" / f"{WEEK}-{socket.gethostname()}.json"


def test_aggregate_no_privacy_leak(tmp_path):
    _write_invocations(
        tmp_path,
        [{"session": "d6f7-secret-session", "query_hash": "deadbeef0123",
          "top_score": 0.9, "n_results": 2}],
    )
    _write_nudges(tmp_path, ["d6f7-secret-session"])

    out_path = _run_aggregate_cli(tmp_path)
    text = out_path.read_text()

    assert "deadbeef0123" not in text
    assert "d6f7-secret-session" not in text
    assert "/mnt/" not in text  # abs-path-allowed
    payload = json.loads(text)
    assert "query_hash" not in payload
    assert payload["distinct_sessions"] == 1


def test_aggregate_idempotent(tmp_path):
    _write_invocations(tmp_path, [{}, {"caller": "skill"}])

    out_path = _run_aggregate_cli(tmp_path)
    first = out_path.read_bytes()
    time.sleep(0.01)
    out_path_2 = _run_aggregate_cli(tmp_path)
    second = out_path_2.read_bytes()

    assert out_path == out_path_2
    assert first == second


# ── residency: gitignore split ────────────────────────────────────────────


def test_gitignore_covers_metrics_jsonl():
    def check_ignore(path):
        return subprocess.run(
            ["git", "check-ignore", "-q", path],
            cwd=REPO_ROOT, capture_output=True, check=False,
        ).returncode

    assert check_ignore("data/drive-index-search/metrics/invocations.jsonl") == 0
    assert check_ignore("data/drive-index-search/metrics/nudges.jsonl") == 0
    assert check_ignore("data/drive-index-search/metrics/weekly/2026-W30-hostx.json") == 1
