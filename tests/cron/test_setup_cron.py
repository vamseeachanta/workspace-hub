"""Integration contract for the setup-cron compatibility entrypoint."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SETUP = REPO / "scripts" / "cron" / "setup-cron.sh"


def _fake_crontab(tmp_path: Path, initial: str = "") -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    state = tmp_path / "crontab.txt"
    state.write_text(initial, encoding="utf-8")
    command = bin_dir / "crontab"
    command.write_text(
        "#!/usr/bin/env bash\n"
        "set -eu\n"
        'if [[ "${1:-}" == "-l" ]]; then cat "$FAKE_CRONTAB_STATE"; exit 0; fi\n'
        'if [[ "${1:-}" == "-" ]]; then cat > "$FAKE_CRONTAB_STATE"; exit 0; fi\n'
        "exit 2\n",
        encoding="utf-8",
    )
    command.chmod(0o755)
    return bin_dir, state


def _run_setup(tmp_path: Path, *args: str, initial: str = "") -> tuple[subprocess.CompletedProcess[str], str]:
    bin_dir, state = _fake_crontab(tmp_path, initial)
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bin_dir}:{env['PATH']}",
            "FAKE_CRONTAB_STATE": str(state),
            "HOME": str(tmp_path / "home"),
            "WORKSPACE_HUB": str(REPO),
            "UV_CACHE_DIR": str(tmp_path / "uv-cache"),
            "CRON_BACKUP_DIR": str(tmp_path / "backups"),
        }
    )
    result = subprocess.run(
        ["bash", str(SETUP), *args],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    return result, state.read_text(encoding="utf-8")


def test_setup_cron_has_no_independent_crontab_writer():
    source = SETUP.read_text(encoding="utf-8")

    assert "| crontab -" not in source
    assert 'exec uv run --script "$CRON_APPLY"' in source


def test_setup_cron_machine_windows_exits_before_linux_transaction(tmp_path):
    result, installed = _run_setup(tmp_path, "--machine", "licensed-win-1", "--dry-run")

    assert result.returncode == 0
    assert "Windows Task Scheduler" in result.stdout
    assert installed == ""


def test_setup_cron_rejects_remote_linux_machine(tmp_path):
    result, installed = _run_setup(
        tmp_path, "--machine", "ace-linux-2", "--allow-live-reload"
    )

    assert result.returncode != 0
    assert "refusing to reconcile local crontab" in result.stderr
    assert installed == ""


def test_setup_cron_entrypoint_twice_is_idempotent(tmp_path):
    notification = (
        "30 4 * * * cd /mnt/local-analysis/workspace-hub && "
        'find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true\n'
    )
    deckhand = (
        "0 5 * * 0 PATH=$HOME/.local/bin:$PATH; cd /mnt/local-analysis/workspace-hub && "
        "uv run --no-project --with pyyaml python "
        ".claude/skills/business-marketing/deckhand-api-presence-sync/catalog_delta.py "
        ">> /mnt/local-analysis/workspace-hub/logs/marketing/deckhand.log 2>&1\n"
    )
    initial = notification * 2 + deckhand * 2
    first, installed_once = _run_setup(
        tmp_path,
        "--machine",
        "ace-linux-1",
        "--allow-live-reload",
        initial=initial,
    )
    assert first.returncode == 0, first.stderr + first.stdout

    second_dir = tmp_path / "second"
    second_dir.mkdir()
    second, installed_twice = _run_setup(
        second_dir,
        "--machine",
        "ace-linux-1",
        "--allow-live-reload",
        initial=installed_once,
    )

    assert second.returncode == 0, second.stderr + second.stdout
    assert installed_twice == installed_once
    assert installed_twice.count("find logs/notifications/") == 1
    assert installed_twice.count("deckhand-api-presence-sync/catalog_delta.py") == 1


def test_setup_cron_dry_run_never_writes(tmp_path):
    initial = "0 * * * * echo external\n"
    result, installed = _run_setup(
        tmp_path, "--machine", "ace-linux-1", "--dry-run", initial=initial
    )

    assert result.returncode != 0  # unknown ownership is surfaced fail-closed
    assert installed == initial
