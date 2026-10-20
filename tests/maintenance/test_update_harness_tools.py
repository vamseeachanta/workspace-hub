from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "update-harness-tools.sh"


def _run_update(tmp_path: Path, *args: str, fail: bool = False, hermes_fail: bool = False):
    log = tmp_path / "tools.log"
    startup = tmp_path / "startup.sh"
    # Shell functions take precedence over PATH, including directories added by
    # the updater. Every assistant command is a local stub; no real CLI runs.
    startup.write_text(
        "hermes() { echo hermes >> \"$TOOL_LOG\"; return \"$HERMES_STATUS\"; }\n"
        "claude() { echo first >> \"$TOOL_LOG\"; return \"$FAKE_STATUS\"; }\n"
        "codex() { echo second >> \"$TOOL_LOG\"; }\n"
        "npm() { echo third >> \"$TOOL_LOG\"; }\n"
        "agy() { echo fourth >> \"$TOOL_LOG\"; }\n"
    )
    env = dict(os.environ, BASH_ENV=str(startup), TOOL_LOG=str(log),
               FAKE_STATUS="7" if fail else "0", HERMES_STATUS="7" if hermes_fail else "0")
    result = subprocess.run(["bash", str(SCRIPT), *args], cwd=REPO_ROOT,
                            env=env, text=True, capture_output=True, check=False)
    return result, log.read_text().splitlines() if log.exists() else []


def test_active_runtime_updates_without_retired_integration(tmp_path: Path):
    result, calls = _run_update(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert calls == ["hermes", "first", "second", "third", "fourth"]


def test_dry_run_executes_no_tools(tmp_path: Path):
    result, calls = _run_update(tmp_path, "--dry-run")
    assert result.returncode == 0
    assert calls == []


def test_failure_is_reported_after_remaining_tools_finish(tmp_path: Path):
    result, calls = _run_update(tmp_path, fail=True)
    assert result.returncode == 1
    assert calls == ["hermes", "first", "second", "third", "fourth"]
    assert "FAILED" in result.stdout


def test_runtime_update_failure_is_reported_after_remaining_tools(tmp_path: Path):
    result, calls = _run_update(tmp_path, hermes_fail=True)
    assert result.returncode == 1
    assert calls == ["hermes", "first", "second", "third", "fourth"]
    assert "FAILED" in result.stdout
