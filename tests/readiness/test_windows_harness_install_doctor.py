"""Windows doctor preparation; all mutations use disposable roots.

Expected statuses come from explicit fixture exit statements or the existing
is_reparse_point contract (scripts/lib/reparse_guard.sh), not the doctor output.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = "scripts/windows/harness-install-doctor.sh"
WRAPPER = ROOT / "scripts/windows/harness-install-doctor.ps1"


def _copy(root, relative):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / relative, target)
    return target


def _script(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def bootstrap(tmp_path):
    root = tmp_path / "repo with spaces"
    script = _copy(root, BOOTSTRAP)
    user = tmp_path / "profile with spaces"
    (user / ".local/bin").mkdir(parents=True)
    tools = tmp_path / "tools"
    # cygpath is a controlled converter: its output is the fixture profile.
    _script(tools / "cygpath", 'printf "%s\\n" "$FIXTURE_PROFILE"\n')
    _script(
        root / "scripts/maintenance/harness-install-doctor.sh",
        'printf "%s\\n" "$HOME" "$PWD" "$WORKSPACE_HUB"\n'
        'command -v fixture-user-tool\nexit "${FIXTURE_STATUS:-0}"\n',
    )
    _script(user / ".local/bin/fixture-user-tool", "exit 0\n")
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        PATH=str(tools) + os.pathsep + env["PATH"],
        USERPROFILE="fixture-profile",
        FIXTURE_PROFILE=str(user),
        HOME=str(tmp_path / "incorrect-profile"),
        WORKSPACE_HUB=str(tmp_path / "incorrect-repository"),
    )
    return root, script, user, env


def _run_bootstrap(bootstrap, tmp_path):
    _, script, _, env = bootstrap
    return subprocess.run(
        ["bash", str(script)], env=env, cwd=tmp_path,
        check=False, capture_output=True, text=True, timeout=30,
    )


@pytest.mark.parametrize("status", [0, 7])
def test_bootstrap_binds_profile_repo_user_tools_and_exit(bootstrap, tmp_path, status):
    """Hand calculation: a fixture exiting s must produce wrapper status s."""
    root, _, user, env = bootstrap
    env["FIXTURE_STATUS"] = str(status)
    result = _run_bootstrap(bootstrap, tmp_path)
    assert result.returncode == status, result.stderr
    assert result.stdout.splitlines() == [
        str(user), str(root), str(root), str(user / ".local/bin/fixture-user-tool"),
    ]


@pytest.mark.parametrize("profile", [None, ""])
def test_bootstrap_rejects_missing_profile(bootstrap, tmp_path, profile):
    *_, env = bootstrap
    if profile is None:
        env.pop("USERPROFILE")
    else:
        env["USERPROFILE"] = profile
    result = _run_bootstrap(bootstrap, tmp_path)
    assert result.returncode != 0
    assert not result.stdout


def test_bootstrap_rejects_unresolvable_profile(bootstrap, tmp_path):
    *_, env = bootstrap
    env["FIXTURE_PROFILE"] = str(tmp_path / "absent")
    result = _run_bootstrap(bootstrap, tmp_path)
    assert result.returncode != 0
    assert not result.stdout


@pytest.mark.parametrize("converted", ["", "."])
def test_bootstrap_rejects_empty_or_relative_conversion(bootstrap, tmp_path, converted):
    *_, env = bootstrap
    env["FIXTURE_PROFILE"] = converted
    result = _run_bootstrap(bootstrap, tmp_path)
    assert result.returncode != 0
    assert not result.stdout


def test_bootstrap_rejects_failed_conversion(bootstrap, tmp_path):
    *_, env = bootstrap
    tools = Path(env["PATH"].split(os.pathsep)[0])
    _script(tools / "cygpath", "exit 1\n")
    result = _run_bootstrap(bootstrap, tmp_path)
    assert result.returncode != 0
    assert not result.stdout


@pytest.mark.parametrize("probe_status", [0, 1, 2, None])
def test_doctor_skills_probe_fails_closed_without_mutation(tmp_path, probe_status):
    """Guard contract: 0=reparse, 1=ordinary, 2=unknown. Only 1 is healthy."""
    repo = tmp_path / "repo"
    doctor = _copy(repo, "scripts/maintenance/harness-install-doctor.sh")
    _script(
        repo / "scripts/agents/install-soul-runtime.sh",
        'echo "Summary: 0 created, 1 unchanged, 0 backed-up, 0 skipped, 0 needs-attention."\n',
    )
    if probe_status is not None:
        _script(
            repo / "scripts/lib/reparse_guard.sh",
            f"is_reparse_point() {{ return {probe_status}; }}\n",
        )
    for name in ("AGENTS.runtime.md", "MEMORY.runtime.md"):
        target = repo / "config/agents/codex" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture runtime\n", encoding="utf-8")
    user = tmp_path / "user"
    marker = user / ".codex/skills/.system/preserved"
    marker.parent.mkdir(parents=True)
    marker.write_bytes(b"preserved")
    env = dict(os.environ, HOME=str(user))
    result = subprocess.run(
        ["bash", str(doctor)], env=env, check=False, capture_output=True, text=True, timeout=30,
    )
    expected = 0 if probe_status == 1 else 1
    assert result.returncode == expected, result.stdout + result.stderr
    assert marker.read_bytes() == b"preserved"
    assert not marker.parent.parent.is_symlink()


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell and Git Bash required")
@pytest.mark.parametrize("status", [0, 7])
def test_native_wrapper_logs_and_propagates_status(tmp_path, status):
    """Fixture exits s; the wrapper must log its output and return exactly s."""
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    bash = shutil.which("bash")
    assert powershell and bash
    root = tmp_path / "repo with spaces"
    _script(root / BOOTSTRAP, f"echo fixture-doctor-output\necho fixture-doctor-error >&2\nexit {status}\n")
    result = subprocess.run(
        [powershell, "-NoProfile", "-File", str(WRAPPER),
         "-WorkspaceRoot", str(root), "-GitBashPath", bash],
        check=False, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == status, result.stderr
    logs = list((root / "logs/maintenance").glob("harness-install-doctor-*.log"))
    assert len(logs) == 1
    log = logs[0].read_text(encoding="utf-8")
    assert "fixture-doctor-output" in log
    assert "fixture-doctor-error" in log
