"""Tests for scripts/windows/agent-preflight.ps1 (#3973 R5).

The preflight writes a JSON capability receipt at session start so agents stop
rediscovering the same Windows faults. Secrets must never appear in it. Every
test runs under each available host: pwsh 7 and Windows PowerShell 5.1.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "windows" / "agent-preflight.ps1"
HOSTS = [h for h in (shutil.which("pwsh"), shutil.which("powershell")) if h]

pytestmark = pytest.mark.skipif(sys.platform != "win32" or not HOSTS, reason="Windows PowerShell host required")


@pytest.fixture(params=HOSTS or [None], ids=lambda h: Path(h).stem if h else "none")
def host(request):
    return request.param


def run(host, tmp_path, env_extra=None, path_prefix=None, *args):
    out = tmp_path / "receipt.json"
    if out.exists():
        out.unlink()
    env = dict(os.environ)
    env.update(env_extra or {})
    if path_prefix:
        env["PATH"] = str(path_prefix) + os.pathsep + env["PATH"]
    r = subprocess.run([host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
                        "-OutFile", str(out), *args], capture_output=True, text=True, env=env, timeout=240)
    receipt = json.loads(out.read_text(encoding="utf-8-sig")) if out.exists() else None
    return r, receipt


def ids(receipt):
    return {f["id"] for f in receipt["findings"]}


def stub_dir(tmp_path):
    d = tmp_path / "Microsoft" / "WindowsApps"
    d.mkdir(parents=True, exist_ok=True)
    (d / "python.exe").write_bytes(b"")  # zero-byte, like the Store execution alias
    return d


def test_receipt_has_schema_and_sections(host, tmp_path):
    r, receipt = run(host, tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["schema"] == "agent-preflight/1"
    for key in ("generated_at", "python", "encoding", "shells", "git", "gh", "clis", "findings"):
        assert key in receipt, key
    for f in receipt["findings"]:
        assert f["severity"] in ("error", "warn", "info") and f["id"] and f["message"]
    # Git Bash is located from git.exe, so per-user installs (AppData\Local\Programs\Git) are found too.
    git = receipt["git"]["path"]
    if git:
        root = Path(git).parents[1]
        if (root / "bin" / "bash.exe").is_file() or (root / "usr" / "bin" / "bash.exe").is_file():
            assert receipt["shells"]["git_bash"] and Path(receipt["shells"]["git_bash"]).is_file()


def test_windowsapps_python_stub_is_flagged_and_skipped(host, tmp_path):
    r, receipt = run(host, tmp_path, path_prefix=stub_dir(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["python"]["path_python_is_store_stub"] is True
    assert "PYTHON_STORE_STUB" in ids(receipt)
    # the first non-stub python on PATH is selected, not the stub
    if receipt["python"]["selected"]:
        assert "WindowsApps" not in receipt["python"]["selected"]


def test_explicit_store_stub_selection_is_an_error(host, tmp_path):
    stub = stub_dir(tmp_path) / "python.exe"
    r, receipt = run(host, tmp_path, None, None, "-Python", str(stub))
    assert "PYTHON_SELECTED_IS_STORE_STUB" in ids(receipt)


def test_named_interpreter_is_used_and_missing_venv_cfg_is_flagged(host, tmp_path):
    venv = tmp_path / "brokenvenv"
    (venv / "Scripts").mkdir(parents=True)
    shutil.copy(sys.executable, venv / "Scripts" / "python.exe")  # copied binary, no pyvenv.cfg
    r, receipt = run(host, tmp_path, None, None, "-Python", str(venv / "Scripts" / "python.exe"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["python"]["selected"].lower().endswith("python.exe")
    assert "VENV_NO_PYVENV_CFG" in ids(receipt)


def test_silent_python_is_not_reported_usable(host, tmp_path):
    d = tmp_path / "silent"
    d.mkdir()
    (d / "python.cmd").write_text("@echo off\r\nexit /b 0\r\n", encoding="ascii")
    r, receipt = run(host, tmp_path, None, None, "-Python", str(d / "python.cmd"))
    assert receipt["python"]["version"] is None
    assert "PYTHON_PROBE_EMPTY" in ids(receipt)


def test_secret_values_never_written(host, tmp_path):
    token = "ghp_preflightSECRETvalue123"
    r, receipt = run(host, tmp_path, {"GH_TOKEN": token})
    text = json.dumps(receipt)
    assert token not in text and token not in r.stdout and token not in r.stderr
    assert receipt["gh"]["gh_token_env_present"] is True


def test_probe_output_echoing_a_token_is_redacted(host, tmp_path):
    token = "github_pat_11ABCDEFG0123456789_abcdefghijklmnop"
    d = tmp_path / "leaky"
    d.mkdir()
    (d / "codex.cmd").write_text("@echo off\r\necho codex-cli 1.0 " + token + "\r\n", encoding="ascii")
    r, receipt = run(host, tmp_path, None, d)
    assert token not in json.dumps(receipt)
    assert "[REDACTED]" in receipt["clis"]["codex"]["version"]


def _fake_gh(tmp_path, status_exit, api_exit):
    d = tmp_path / "fakegh"
    d.mkdir(exist_ok=True)
    (d / "gh.cmd").write_text(
        "@echo off\r\n"
        'if "%1"=="auth" exit /b ' + str(status_exit) + "\r\n"
        'if "%1"=="api" (echo someone& exit /b ' + str(api_exit) + ")\r\n"
        "echo gh version 9.9.9\r\nexit /b 0\r\n", encoding="ascii")
    return d


def test_stale_inactive_gh_account_is_not_reported_as_unauthenticated(host, tmp_path):
    # `gh auth status` exits 1 when ANY stored account is invalid, even while the active one works.
    r, receipt = run(host, tmp_path, None, _fake_gh(tmp_path, status_exit=1, api_exit=0))
    assert r.returncode == 0, r.stdout + r.stderr
    assert receipt["gh"]["version"] == "gh version 9.9.9"  # proves the .cmd fixture actually ran
    assert receipt["gh"]["auth_ok"] is True
    assert "GH_NOT_AUTHENTICATED" not in ids(receipt)
    assert "GH_STALE_STORED_ACCOUNT" in ids(receipt)


def test_failed_api_call_is_reported_unauthenticated(host, tmp_path):
    r, receipt = run(host, tmp_path, None, _fake_gh(tmp_path, status_exit=1, api_exit=1))
    assert receipt["gh"]["version"] == "gh version 9.9.9"
    assert receipt["gh"]["auth_ok"] is False
    assert "GH_NOT_AUTHENTICATED" in ids(receipt)


def test_cli_version_read_past_powershell_shim(host, tmp_path):
    # npm installs drop codex.ps1 next to codex.cmd; the .ps1 must not hide the runnable .cmd.
    d = tmp_path / "npmbin"
    d.mkdir()
    (d / "codex.ps1").write_text("Write-Output 'shim'\n", encoding="ascii")
    (d / "codex.cmd").write_text("@echo off\r\necho codex-cli 9.8.7\r\n", encoding="ascii")
    r, receipt = run(host, tmp_path, None, d)
    assert receipt["clis"]["codex"]["version"] == "codex-cli 9.8.7"


def test_probe_is_bounded_when_a_child_holds_the_pipes(host, tmp_path):
    # The parent exits at once while a detached child keeps stdout open for 60 s.
    d = tmp_path / "hang"
    d.mkdir()
    (d / "codex.cmd").write_text("@echo off\r\nstart /b ping -n 60 127.0.0.1\r\nexit /b 0\r\n", encoding="ascii")
    r, receipt = run(host, tmp_path, None, d, "-TimeoutSec", "5")
    assert receipt is not None and r.returncode == 0, r.stdout + r.stderr
    assert receipt["clis"]["codex"]["version"] in (None, "timeout")


def test_strict_mode_exits_nonzero_on_error_finding(host, tmp_path):
    missing = tmp_path / "nope" / "python.exe"
    r, receipt = run(host, tmp_path, None, stub_dir(tmp_path), "-Python", str(missing), "-Strict")
    assert "PYTHON_SELECTED_MISSING" in ids(receipt)
    assert r.returncode == 1
