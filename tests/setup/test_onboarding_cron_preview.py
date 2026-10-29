"""Isolated onboarding-preview contract for issue #3490.

The issue specifies arbitrary protocol statuses: zero succeeds and seven fails.
Only Bash and read-only filesystem utilities are real; all mutating commands
and sibling setup scripts reject execution inside a disposable fixture tree.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess


REPO = Path(__file__).resolve().parent.parent.parent
SETUP = REPO / "scripts" / "setup" / "new-machine-setup.sh"
SUCCESS = 0  # Issue #3490: successful stub completion.
FAILURE = 7  # Issue #3490: deliberately failed preview, also used for rejection.


def _executable(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _snapshot(*roots: Path) -> dict[Path, tuple[int, bytes | None]]:
    return {
        path: (path.stat().st_mode, path.read_bytes() if path.is_file() else None)
        for root in roots
        for path in (root, *root.rglob("*"))
    }


def _run_preview(tmp_path: Path, status: int, *flags: str):
    workspace = tmp_path / "workspace"
    setup = workspace / "scripts" / "setup" / SETUP.name
    setup.parent.mkdir(parents=True)
    # Run the shipped entrypoint unchanged, with its derived root in the fixture.
    setup.write_bytes(SETUP.read_bytes())
    user_dir = tmp_path / "user"
    user_dir.mkdir()
    (user_dir / ".bashrc").write_text("# existing shell config\n", encoding="utf-8")
    (user_dir / ".ssh").mkdir()
    (workspace / ".env.example").write_text("# preview fixture\n", encoding="utf-8")
    state = tmp_path / "state"
    state.mkdir()
    (state / "scheduler").write_text("existing scheduler state\n", encoding="utf-8")
    (state / "unrelated").write_text("preserve unrelated state\n", encoding="utf-8")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # No inherited PATH fallback: an unexpected command cannot reach the host.
    for command in ("bash", "dirname", "grep", "ls"):
        real_command = shutil.which(command)
        assert real_command is not None, f"required fixture utility: {command}"
        (bin_dir / command).symlink_to(real_command)
    _executable(bin_dir / "uname", "#!/bin/bash\necho Linux\n")
    _executable(bin_dir / "hostname", "#!/bin/bash\necho fixture\n")
    _executable(bin_dir / "date", "#!/bin/bash\necho fixture-date\n")

    rejected = tmp_path / "rejected-calls"
    rejected.write_text("", encoding="utf-8")
    reject_script = (
        '#!/bin/bash\nprintf "%s\\n" "$0 $*" >> "$REJECTED_CALLS"\n'
        'exit "$REJECT_STATUS"\n'
    )
    for command in (
        "git", "npm", "npx", "node", "pip", "pip3", "uv", "python", "python3",
        "claude", "codex", "gemini", "hermes", "gh", "ssh-keygen", "ssh-copy-id",
        "crontab", "systemctl", "schtasks", "launchctl", "sudo", "apt", "apt-get",
        "brew", "curl", "wget", "cp", "mkdir", "ln", "chmod", "install", "tmux",
    ):
        _executable(bin_dir / command, reject_script)
    for script in (
        "scripts/setup/install-all-hooks.sh",
        "scripts/install/pin-codex.sh",
        "scripts/setup/deploy-tmux.sh",
        "scripts/memory/bootstrap-machine.sh",
        "scripts/setup/lib/install-provider-clis.sh",
        "scripts/setup/lib/orchestrate-auth.sh",
        "scripts/setup/lib/instantiate-hermes-config.sh",
        "scripts/setup/emit-machine-status.sh",
        "scripts/setup/verify-setup.sh",
    ):
        _executable(workspace / script, reject_script)

    cron_calls = tmp_path / "cron-calls"
    cron_calls.write_text("", encoding="utf-8")
    _executable(
        workspace / "scripts" / "cron" / "setup-cron.sh",
        '#!/bin/bash\nset -eu\n'
        'printf "%s\\n" invoke "$@" >> "$CRON_CALLS"\n'
        # The sentinel rejects a live installer call before any work can occur.
        'if [[ " $* " != *" --dry-run "* ]]; then\n'
        '  printf "%s\\n" "cron without --dry-run" >> "$REJECTED_CALLS"\n'
        '  exit "$REJECT_STATUS"\n'
        'fi\n'
        'echo "cron fixture diagnostic" >&2\n'
        'exit "$CRON_STATUS"\n',
    )
    before = _snapshot(workspace, user_dir, state)
    env = {
        "HOME": str(user_dir),
        "PATH": str(bin_dir),
        "LC_ALL": "C",
        "TMPDIR": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": os.environ["UV_CACHE_DIR"],
        "REJECTED_CALLS": str(rejected),
        "REJECT_STATUS": str(FAILURE),
        "CRON_CALLS": str(cron_calls),
        "CRON_STATUS": str(status),
    }
    result = subprocess.run(
        [str(bin_dir / "bash"), str(setup), "--dry-run", *flags],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,  # Fixture safety budget, independent of production timing.
    )
    assert rejected.read_text(encoding="utf-8") == "", result.stdout + result.stderr
    assert _snapshot(workspace, user_dir, state) == before
    return result, cron_calls.read_text(encoding="utf-8").splitlines()


def test_failed_cron_preview_is_reported_and_returns_nonzero(tmp_path):
    result, calls = _run_preview(tmp_path, FAILURE)

    assert calls == ["invoke", "--dry-run"]
    assert result.returncode == FAILURE
    assert "cron preview failed" in result.stderr.lower()
    assert f"status {FAILURE}" in result.stderr
    assert "cron fixture diagnostic" in result.stderr
    assert "Submodule initialisation" in result.stdout
    assert "git submodule update --init --recursive" in result.stdout
    assert "Setup complete!" not in result.stdout + result.stderr


def test_successful_preview_passes_dry_run_once(tmp_path):
    result, calls = _run_preview(tmp_path, SUCCESS)

    assert result.returncode == SUCCESS, result.stdout + result.stderr
    assert calls == ["invoke", "--dry-run"]
    assert "Setup complete!" in result.stdout


def test_no_cron_performs_no_installer_call(tmp_path):
    result, calls = _run_preview(tmp_path, FAILURE, "--no-cron")

    assert result.returncode == SUCCESS, result.stdout + result.stderr
    assert calls == []
    assert "Skipped (--no-cron flag)." in result.stdout
    assert "Setup complete!" in result.stdout


def test_preview_cannot_reach_live_scheduler_or_installation(tmp_path):
    # _run_preview rejects external mutations and compares all fixture state,
    # including scheduler and unrelated sentinels, on both completion paths.
    for status in (SUCCESS, FAILURE):
        case = tmp_path / str(status)
        case.mkdir()
        result, calls = _run_preview(case, status)

        assert result.returncode == status
        assert calls == ["invoke", "--dry-run"]
