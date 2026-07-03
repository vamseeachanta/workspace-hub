"""Tests for scripts/enforcement/check-memory-index-size.sh (wh#3366).

Guards the Claude Code auto-memory index (MEMORY.md) against the harness's
BYTE-size load cap — the gap that let the index silently grow to 52KB and
drop its long tail from recall while compact-memory.py's LINE-based limit
(180) never fired.

Fixture strategy: each test writes a MEMORY.md of a controlled byte size to
tmp_path and invokes the script in positional-args mode (which bypasses the
~/.claude auto-detect), so tests are hermetic and independent of host state.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-memory-index-size.sh"


def _write_index(path: Path, kib: float) -> Path:
    """Write a MEMORY.md of approximately `kib` KiB using whole index lines."""
    line = "- [Topic](topic-file.md) — a representative one-line index hook entry\n"
    target = int(kib * 1024)
    body = ""
    while len(body.encode()) < target:
        body += line
    path.write_text(body)
    return path


def _run(*args: str, env_extra: dict | None = None):
    import os

    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def test_under_target_passes_quietly(tmp_path: Path):
    idx = _write_index(tmp_path / "MEMORY.md", kib=10)
    r = _run(str(idx))
    assert r.returncode == 0
    assert r.stderr.strip() == ""


def test_over_target_under_cap_warns_but_passes(tmp_path: Path):
    idx = _write_index(tmp_path / "MEMORY.md", kib=20)  # >17 target, <24 cap
    r = _run(str(idx))
    assert r.returncode == 0, r.stderr
    assert "target" in r.stderr.lower()


def test_at_or_over_hard_cap_fails(tmp_path: Path):
    idx = _write_index(tmp_path / "MEMORY.md", kib=30)  # >= 24 cap
    r = _run(str(idx))
    assert r.returncode == 1
    assert "load cap" in r.stderr.lower()
    assert "dropped" in r.stderr.lower()


def test_bypass_env_downgrades_hard_failure(tmp_path: Path):
    idx = _write_index(tmp_path / "MEMORY.md", kib=30)
    r = _run(str(idx), env_extra={"ALLOW_MEMORY_INDEX_OVERSIZE": "1"})
    assert r.returncode == 0
    assert "bypass" in r.stderr.lower()


def test_custom_thresholds_respected(tmp_path: Path):
    idx = _write_index(tmp_path / "MEMORY.md", kib=12)
    # Lower the hard cap below the file size -> should now fail.
    r = _run("--hard-kib=10", str(idx))
    assert r.returncode == 1


def test_missing_positional_file_is_usage_error(tmp_path: Path):
    r = _run(str(tmp_path / "does-not-exist.md"))
    assert r.returncode == 2


def test_multiple_indices_one_over_cap_fails(tmp_path: Path):
    ok = _write_index(tmp_path / "a-MEMORY.md", kib=8)
    bad = _write_index(tmp_path / "b-MEMORY.md", kib=28)
    r = _run(str(ok), str(bad))
    assert r.returncode == 1
    assert "b-MEMORY.md" in r.stderr
    assert "a-MEMORY.md" not in r.stderr


def test_no_positional_args_never_errors_on_absent_indices(tmp_path: Path):
    # With no args it scans ~/.claude/projects/*/memory/MEMORY.md; whatever the
    # host state, the script must not crash (exit 0 or 1, never a bash error).
    r = _run()
    assert r.returncode in (0, 1)
