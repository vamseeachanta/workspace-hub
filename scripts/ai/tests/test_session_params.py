"""Tests for session-params.py helper."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "session-params.py"
WS_ROOT = Path(__file__).parents[3]


def run_script(env=None) -> list[dict]:
    """Run session-params.py and return parsed JSONL lines."""
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(SCRIPT)],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
        cwd=str(WS_ROOT),
    )
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def test_session_params_output_structure():
    """T1: script outputs 3 JSONL lines with required keys."""
    rows = run_script()
    assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}: {rows}"
    required = {"event", "provider", "model", "context_k", "effort", "ts"}
    for row in rows:
        missing = required - set(row.keys())
        assert not missing, f"Row missing keys {missing}: {row}"
    assert all(r["event"] == "session_params" for r in rows)
    providers = {r["provider"] for r in rows}
    assert providers == {"claude", "codex", "gemini"}


def test_session_params_context_k_is_positive_int():
    """T1b: context_k is a positive integer."""
    rows = run_script()
    for r in rows:
        assert isinstance(r["context_k"], int), f"context_k not int: {r}"
        assert r["context_k"] > 0


def test_session_params_missing_config_graceful():
    """T2: graceful output when HOME points to empty temp dir — no crash, 3 lines."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rows = run_script(env={"HOME": tmpdir})
    assert len(rows) == 3
    for row in rows:
        assert row.get("event") == "session_params"
        assert row.get("provider") in {"claude", "codex", "gemini"}
        assert "model" in row
        assert isinstance(row.get("context_k"), int)
