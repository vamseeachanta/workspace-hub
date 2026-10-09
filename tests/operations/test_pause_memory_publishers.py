from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SH = REPO / "scripts" / "operations" / "pause-memory-publishers.sh"
PS1 = REPO / "scripts" / "operations" / "pause-memory-publishers.ps1"


def _write_fake_crontab(tmp_path: Path, initial: str) -> tuple[Path, Path]:
    state = tmp_path / "crontab.txt"
    state.write_text(initial, encoding="utf-8")
    fake = tmp_path / "crontab"
    fake.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail
state={state}
if [[ "${{1:-}}" == "-l" ]]; then
  cat "$state"
  exit 0
fi
if [[ "${{1:-}}" == "-" ]]; then
  cat > "$state"
  exit 0
fi
cp "$1" "$state"
""",
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return fake, state


def _run(tmp_path: Path, fake: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update(
        {
            "CRONTAB_BIN": str(fake),
            "HOME": str(tmp_path),
            "PAUSE_MEMORY_DATE": "20261009-134400",
        }
    )
    return subprocess.run(["bash", str(SH), *args], capture_output=True, text=True, env=env)


def test_pause_cron_check_is_non_mutating(tmp_path: Path):
    fake, state = _write_fake_crontab(
        tmp_path,
        "0 2 * * * bash scripts/cron/comprehensive-learning-nightly.sh\n"
        "25 4 * * * bash scripts/memory/bridge-hermes-claude.sh --commit\n",
    )

    result = _run(tmp_path, fake, "--check")

    assert result.returncode == 0
    assert "would pause" in result.stdout
    assert "#PAUSED-X02" not in state.read_text(encoding="utf-8")


def test_pause_cron_apply_backs_up_and_comments_targets(tmp_path: Path):
    fake, state = _write_fake_crontab(
        tmp_path,
        "0 2 * * * bash scripts/cron/comprehensive-learning-nightly.sh\n"
        "25 4 * * * bash scripts/memory/bridge-hermes-claude.sh --commit\n"
        "0 6 * * * bash scripts/other.sh\n",
    )

    result = _run(tmp_path, fake, "--apply")

    assert result.returncode == 0, result.stderr
    backup = tmp_path / "crontab.bak-20261009-134400"
    assert backup.exists()
    assert "comprehensive-learning-nightly.sh" in backup.read_text(encoding="utf-8")
    updated = state.read_text(encoding="utf-8")
    assert "#PAUSED-X02 0 2 * * * bash scripts/cron/comprehensive-learning-nightly.sh" in updated
    assert "#PAUSED-X02 25 4 * * * bash scripts/memory/bridge-hermes-claude.sh --commit" in updated
    assert "scripts/other.sh" in updated


def test_pause_cron_undo_removes_marker(tmp_path: Path):
    fake, state = _write_fake_crontab(
        tmp_path,
        "#PAUSED-X02 0 2 * * * bash scripts/cron/comprehensive-learning-nightly.sh\n"
        "#PAUSED-X02 25 4 * * * bash scripts/memory/bridge-hermes-claude.sh --commit\n",
    )

    result = _run(tmp_path, fake, "--undo")

    assert result.returncode == 0, result.stderr
    updated = state.read_text(encoding="utf-8")
    assert "#PAUSED-X02" not in updated
    assert "bridge-hermes-claude.sh --commit" in updated


def test_windows_pause_script_uses_task_definition_backup_and_disable_enable():
    text = PS1.read_text(encoding="utf-8")

    assert 'TaskName = "MemoryBridgeSync"' in text
    assert "Export-ScheduledTask" in text
    assert "SCHTASKS_BIN" in text
    assert "/Query /TN" in text
    assert "/XML" in text
    assert "LASTEXITCODE" in text
    assert "Failed to back up" in text
    assert "Disable-ScheduledTask" in text
    assert "Enable-ScheduledTask" in text
    assert "PAUSE_MEMORY_TASK_BACKUP_DIR" in text
