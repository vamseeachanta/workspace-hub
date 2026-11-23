"""
CI smoke: review-gate hook runs without uv on PATH.

Issue #2532. scripts/enforcement/require-review-on-push.sh historically used
`uv run --no-project python` for ms-precision timestamps (latency telemetry).
This made uv a hard dependency of the pre-push hook on every developer
machine. The fix: replace uv calls with `date +%s%3N` → python3 → seconds*1000
fallback chain. This smoke test verifies that fix holds.

Skip on macOS where `date +%s%3N` returns the literal `%3N` string (BSD date).

Run with: PYTHONPATH=src python3 -m pytest tests/ci_smoke/test_review_gate_no_uv_dependency.py -v
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/enforcement/require-review-on-push.sh"
LATENCY_LOG = REPO_ROOT / "logs/hooks/review-gate-latency.jsonl"


def _scrubbed_path() -> str:
    """
    Build a PATH that excludes any directory containing a `uv` binary.
    Keeps system-essential dirs (/usr/bin, /bin, /usr/local/bin minus uv).
    """
    path_dirs = os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
    kept: list[str] = []
    for d in path_dirs:
        candidate = Path(d) / "uv"
        if candidate.exists():
            continue
        kept.append(d)
    if not kept:
        kept = ["/usr/bin", "/bin"]
    return os.pathsep.join(kept)


def test_review_gate_succeeds_without_uv_on_path():
    """
    Run the review-gate script with PATH scrubbed of any directory containing
    a `uv` binary. The script must exit 0 (or with a deterministic non-uv
    error) and a new latency JSONL entry must be written.

    HEAD HEAD args mean "no commits to check" — script should PASS quickly
    and append exactly one latency entry.
    """
    if platform.system() == "Darwin":
        pytest.skip("macOS BSD date does not support +%3N; ms-precision path requires python3 fallback only")

    # Note: invoke via `bash <script>` (not `./<script>`), so executable bit is
    # not required. GitHub's actions/checkout@v4 does not preserve +x on script
    # files, and other workflow steps already chmod +x before direct invocation.
    assert SCRIPT.exists(), f"Script missing: {SCRIPT}"

    LATENCY_LOG.parent.mkdir(parents=True, exist_ok=True)
    pre_lines = LATENCY_LOG.read_text().splitlines() if LATENCY_LOG.exists() else []

    env = os.environ.copy()
    env["PATH"] = _scrubbed_path()
    env.pop("VIRTUAL_ENV", None)
    env["REVIEW_GATE_STRICT"] = "0"

    assert shutil.which("uv", path=env["PATH"]) is None, (
        f"PATH scrub failed; uv still resolvable in: {env['PATH']}"
    )

    result = subprocess.run(
        ["bash", str(SCRIPT), "HEAD", "HEAD"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Script exited {result.returncode} with uv removed from PATH.\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    assert "uv: command not found" not in result.stderr, (
        f"Script still depends on uv: {result.stderr!r}"
    )

    post_lines = LATENCY_LOG.read_text().splitlines() if LATENCY_LOG.exists() else []
    assert len(post_lines) == len(pre_lines) + 1, (
        f"Expected 1 new latency entry; pre={len(pre_lines)} post={len(post_lines)}"
    )


def test_review_gate_writes_latency_telemetry_shape():
    """
    Last latency JSONL line must parse as JSON and contain the expected
    schema: {timestamp, branch, strict, verdict, latency_ms} with latency_ms
    an int. Guards against schema drift breaking the audit cron downstream.
    """
    if platform.system() == "Darwin":
        pytest.skip("Paired test skipped on macOS; covered by python3 fallback path")

    LATENCY_LOG.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PATH"] = _scrubbed_path()
    env.pop("VIRTUAL_ENV", None)
    env["REVIEW_GATE_STRICT"] = "0"

    result = subprocess.run(
        ["bash", str(SCRIPT), "HEAD", "HEAD"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Script run failed: stderr={result.stderr!r}"

    assert LATENCY_LOG.exists(), f"Latency log not created at {LATENCY_LOG}"
    last_line = LATENCY_LOG.read_text().splitlines()[-1]
    entry = json.loads(last_line)

    required_keys = {"timestamp", "branch", "strict", "verdict", "latency_ms"}
    missing = required_keys - set(entry.keys())
    assert not missing, f"Missing required keys: {missing}; full entry: {entry}"

    assert isinstance(entry["latency_ms"], int), (
        f"latency_ms must be int, got {type(entry['latency_ms']).__name__}: {entry['latency_ms']!r}"
    )
    assert entry["latency_ms"] >= 0, f"latency_ms negative: {entry['latency_ms']}"
