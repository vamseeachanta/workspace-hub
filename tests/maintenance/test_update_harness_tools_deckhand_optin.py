from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "update-harness-tools.sh"


def _run_update(tmp_path: Path, *args: str, fail: bool = False):
    log = tmp_path / "tools.log"
    startup = tmp_path / "startup.sh"
    # Shell functions take precedence over PATH, including directories added by
    # the updater. Every assistant command is a local stub; no real CLI runs.
    startup.write_text(
        "hermes() { echo forbidden >> \"$TOOL_LOG\"; return 99; }\n"
        "claude() { echo first >> \"$TOOL_LOG\"; return \"$FAKE_STATUS\"; }\n"
        "codex() { echo second >> \"$TOOL_LOG\"; }\n"
        "npm() { echo third >> \"$TOOL_LOG\"; }\n"
        "agy() { echo fourth >> \"$TOOL_LOG\"; }\n"
    )
    env = dict(os.environ, BASH_ENV=str(startup), TOOL_LOG=str(log),
               FAKE_STATUS="7" if fail else "0", DECKHAND_PATCHES="1",
               DECKHAND_HERMES_INSTALLER=str(tmp_path / "absent-installer"),
               DECKHAND_HEALTH_CHECK=str(tmp_path / "absent-health.py"))
    result = subprocess.run(["bash", str(SCRIPT), *args], cwd=REPO_ROOT,
                            env=env, text=True, capture_output=True, check=False)
    return result, log.read_text().splitlines() if log.exists() else []


def test_retired_gateway_is_never_updated_even_with_legacy_opt_in(tmp_path: Path):
    result, calls = _run_update(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert calls == ["first", "second", "third", "fourth"]


def test_dry_run_executes_no_tools(tmp_path: Path):
    result, calls = _run_update(tmp_path, "--dry-run")
    assert result.returncode == 0
    assert calls == []


def test_failure_is_reported_after_remaining_tools_finish(tmp_path: Path):
    result, calls = _run_update(tmp_path, fail=True)
    assert result.returncode == 1
    assert calls == ["first", "second", "third", "fourth"]
    assert "FAILED" in result.stdout
