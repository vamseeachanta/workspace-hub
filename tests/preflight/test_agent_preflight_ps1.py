"""Tests for scripts/windows/agent-preflight.ps1 (#3973 R5).

The preflight writes a JSON capability receipt at session start so agents stop
rediscovering the same Windows faults. Secrets must never appear in it.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "windows" / "agent-preflight.ps1"
PWSH = shutil.which("pwsh") or shutil.which("powershell")

pytestmark = pytest.mark.skipif(sys.platform != "win32" or not PWSH, reason="Windows PowerShell host required")


def run(tmp_path, env_extra=None, path_prefix=None, *args):
    out = tmp_path / "receipt.json"
    env = dict(os.environ)
    env.update(env_extra or {})
    if path_prefix:
        env["PATH"] = str(path_prefix) + os.pathsep + env["PATH"]
    r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), "-OutFile", str(out), *args],
                       capture_output=True, text=True, env=env, timeout=180)
    receipt = json.loads(out.read_text(encoding="utf-8-sig")) if out.exists() else None
    return r, receipt


def ids(receipt):
    return {f["id"] for f in receipt["findings"]}


def test_receipt_has_schema_and_sections(tmp_path):
    r, receipt = run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["schema"] == "agent-preflight/1"
    for key in ("generated_at", "python", "encoding", "shells", "git", "gh", "clis", "findings"):
        assert key in receipt, key
    for f in receipt["findings"]:
        assert f["severity"] in ("error", "warn", "info") and f["id"] and f["message"]
    # Git Bash is located from git.exe, so per-user installs (AppData\Local\Programs\Git) are found too.
    if receipt["git"]["path"]:
        assert receipt["shells"]["git_bash"] and Path(receipt["shells"]["git_bash"]).is_file()


def test_windowsapps_python_stub_is_flagged(tmp_path):
    stub_dir = tmp_path / "Microsoft" / "WindowsApps"
    stub_dir.mkdir(parents=True)
    (stub_dir / "python.exe").write_bytes(b"")  # zero-byte, like the Store execution alias
    r, receipt = run(tmp_path, path_prefix=stub_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["python"]["path_python_is_store_stub"] is True
    assert "PYTHON_STORE_STUB" in ids(receipt)


def test_named_interpreter_is_used_and_missing_venv_cfg_is_flagged(tmp_path):
    venv = tmp_path / "brokenvenv"
    (venv / "Scripts").mkdir(parents=True)
    shutil.copy(sys.executable, venv / "Scripts" / "python.exe")  # copied binary, no pyvenv.cfg
    r, receipt = run(tmp_path, None, None, "-Python", str(venv / "Scripts" / "python.exe"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["python"]["selected"].lower().endswith("python.exe")
    assert "VENV_NO_PYVENV_CFG" in ids(receipt)


def test_secret_values_never_written(tmp_path):
    token = "ghp_preflightSECRETvalue123"
    r, receipt = run(tmp_path, {"GH_TOKEN": token})
    text = json.dumps(receipt)
    assert token not in text and token not in r.stdout and token not in r.stderr
    assert receipt["gh"]["gh_token_env_present"] is True


def _fake_gh(tmp_path, status_exit, api_exit):
    d = tmp_path / "fakegh"
    d.mkdir()
    (d / "gh.cmd").write_text(
        "@echo off\r\n"
        'if "%1"=="auth" exit /b ' + str(status_exit) + "\r\n"
        'if "%1"=="api" (echo someone& exit /b ' + str(api_exit) + ")\r\n"
        "echo gh version 9.9.9\r\nexit /b 0\r\n", encoding="ascii")
    return d


def test_stale_inactive_gh_account_is_not_reported_as_unauthenticated(tmp_path):
    # `gh auth status` exits 1 when ANY stored account is invalid, even while the active one works.
    r, receipt = run(tmp_path, None, _fake_gh(tmp_path, status_exit=1, api_exit=0))
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["gh"]["auth_ok"] is True
    assert "GH_NOT_AUTHENTICATED" not in ids(receipt)
    assert "GH_STALE_STORED_ACCOUNT" in ids(receipt)


def test_failed_api_call_is_reported_unauthenticated(tmp_path):
    r, receipt = run(tmp_path, None, _fake_gh(tmp_path, status_exit=1, api_exit=1))
    assert receipt["gh"]["auth_ok"] is False
    assert "GH_NOT_AUTHENTICATED" in ids(receipt)


def test_strict_mode_exits_nonzero_on_error_finding(tmp_path):
    stub_dir = tmp_path / "Microsoft" / "WindowsApps"
    stub_dir.mkdir(parents=True)
    (stub_dir / "python.exe").write_bytes(b"")
    missing = tmp_path / "nope" / "python.exe"
    r, receipt = run(tmp_path, None, stub_dir, "-Python", str(missing), "-Strict")
    assert "PYTHON_SELECTED_MISSING" in ids(receipt)
    assert r.returncode == 1
