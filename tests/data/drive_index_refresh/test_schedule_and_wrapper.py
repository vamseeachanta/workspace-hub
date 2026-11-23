from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
WRAPPER = REPO_ROOT / "scripts/data/drive-index/refresh-drive-index.sh"


def test_wrapper_notify_on_failure(tmp_path):
    notify = tmp_path / "notify.log"
    env = os.environ.copy()
    env["DRIVE_INDEX_NOTIFY_LOG"] = str(notify)
    env["DRIVE_INDEX_TEST_MODE"] = "1"

    result = subprocess.run(["bash", str(WRAPPER), "bad"], cwd=REPO_ROOT, env=env, text=True, capture_output=True)

    assert result.returncode == 1
    assert "cron\tdrive-index-refresh-bad\tfail" in notify.read_text()


def test_wrapper_uses_flock_guard():
    assert "flock -n" in WRAPPER.read_text()


def test_wrapper_notify_pass_summary(tmp_path):
    notify = tmp_path / "notify.log"
    env = os.environ.copy()
    env["DRIVE_INDEX_NOTIFY_LOG"] = str(notify)
    env["DRIVE_INDEX_TEST_MODE"] = "1"

    result = subprocess.run(["bash", str(WRAPPER), "ace"], cwd=REPO_ROOT, env=env, text=True, capture_output=True)

    assert result.returncode == 0
    assert "cron\tdrive-index-refresh-ace\tpass" in notify.read_text()


def test_schedule_tasks_valid():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/cron/validate-schedule.py")],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    data = yaml.safe_load((REPO_ROOT / "config/scheduled-tasks/schedule-tasks.yaml").read_text())
    tasks = {task["id"]: task for task in data["tasks"]}
    assert tasks["drive-index-refresh-ace"]["machines"] == ["ace-linux-1"]
    assert tasks["drive-index-refresh-dde"]["machines"] == ["dev-secondary", "ace-linux-2"]
    assert tasks["drive-index-refresh-cad"]["machines"] == ["ace-linux-1"]
