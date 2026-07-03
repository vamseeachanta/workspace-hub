"""Tests for scripts/enforcement/check-gh-auth.sh (wh#3368).

The script verifies real GitHub auth via `gh api user` rather than the
unreliable `gh auth status`. Tests stub the gh binary via the GH_BIN env
override so they never touch the network or the host's real credentials.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-gh-auth.sh"


def _fake_gh(tmp_path: Path, *, login: str | None, exit_code: int = 0) -> Path:
    """A stub `gh` that emulates `gh api user -q .login`."""
    body = "#!/usr/bin/env bash\n"
    if login is not None and exit_code == 0:
        body += f'printf "%s\\n" "{login}"\nexit 0\n'
    else:
        body += f"exit {exit_code}\n"
    p = tmp_path / "gh"
    p.write_text(body)
    p.chmod(0o755)
    return p


def _run(*args: str, gh_bin: str | Path):
    env = os.environ.copy()
    env["GH_BIN"] = str(gh_bin)
    return subprocess.run(
        ["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env
    )


def test_valid_auth_passes_and_prints_login(tmp_path: Path):
    gh = _fake_gh(tmp_path, login="vamseeachanta")
    r = _run(gh_bin=gh)
    assert r.returncode == 0
    assert "vamseeachanta" in r.stdout


def test_quiet_suppresses_login_output(tmp_path: Path):
    gh = _fake_gh(tmp_path, login="vamseeachanta")
    r = _run("--quiet", gh_bin=gh)
    assert r.returncode == 0
    assert r.stdout.strip() == ""


def test_invalid_token_fails_with_guidance(tmp_path: Path):
    # gh present but the API call fails (401) — the stale-status trap.
    gh = _fake_gh(tmp_path, login=None, exit_code=1)
    r = _run(gh_bin=gh)
    assert r.returncode == 1
    assert "not working" in r.stderr.lower()
    assert "gh auth login" in r.stderr


def test_empty_login_treated_as_failure(tmp_path: Path):
    gh = _fake_gh(tmp_path, login="")  # exit 0 but empty output
    r = _run(gh_bin=gh)
    assert r.returncode == 1


def test_missing_gh_binary_is_distinct_exit_code(tmp_path: Path):
    r = _run(gh_bin=tmp_path / "definitely-not-here")
    assert r.returncode == 2
    assert "not found" in r.stderr.lower()


def test_unknown_flag_is_usage_error(tmp_path: Path):
    gh = _fake_gh(tmp_path, login="x")
    r = _run("--bogus", gh_bin=gh)
    assert r.returncode == 2
