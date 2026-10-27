"""Hermetic shell-diagnostic regressions for issue #2291.

Reuse the temporary schedule/registry/log/report layout from
scripts/monitoring/tests/test_cron_health_check.sh:setup_temp_workspace.
The daily schedule comes from that fixture; no timing policy is introduced.
Expected counts are hand-counted: one scheduled task, with either one diagnostic
or none. Exit codes follow cron-health-check.sh's documented exit contract.
"""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

import pytest
import yaml


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts" / "monitoring" / "cron-health-check.sh"
)


@pytest.fixture
def monitor(tmp_path, monkeypatch):
    """Run the real monitor with stand-in uv/hostname and synthetic inputs."""
    workspace = tmp_path / "workspace"
    schedule = workspace / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
    registry = workspace / "config" / "workstations" / "registry.yaml"
    log = workspace / "logs" / "dependency.log"
    for directory in (schedule.parent, registry.parent, log.parent):
        directory.mkdir(parents=True, exist_ok=True)
    schedule.write_text(yaml.safe_dump({"tasks": [{
        "id": "dependency-check",
        "label": "Dependency check",
        "schedule": "35 1 * * *",
        "machines": ["fixture"],
        "log": "logs/dependency.log",
        "description": "Synthetic dependency check.",
    }]}))
    registry.write_text(yaml.safe_dump({
        "machines": {"fixture": {"hostname": "fixture"}},
    }))

    # Isolate the directory the monitor prepends to PATH as well as its outputs.
    user_dir = tmp_path / "user"
    bin_dir = user_dir / ".local" / "bin"
    bin_dir.mkdir(parents=True)
    uv = bin_dir / "uv"
    uv.write_text(
        "#!/bin/sh\n"
        '[ "$1 $2 $3" = "run --no-project python" ] || exit 1\n'
        "shift 3\n"
        f'exec {shlex.quote(sys.executable)} "$@"\n'
    )
    hostname = bin_dir / "hostname"
    hostname.write_text("#!/bin/sh\nprintf '%s\\n' fixture\n")
    for command in (uv, hostname):
        command.chmod(command.stat().st_mode | 0o111)
    monkeypatch.setenv("HOME", str(user_dir))

    def run(log_text):
        if log_text is not None:
            log.write_text(log_text)
        result = subprocess.run(
            ["bash", str(SCRIPT_PATH), "--workspace", str(workspace)],
            cwd=tmp_path, env=os.environ.copy(), capture_output=True, text=True,
            check=False,
        )
        assert result.stderr == ""
        reports = list((workspace / ".claude" / "state" / "cron-health").glob("*.json"))
        assert len(reports) == 1  # One monitor invocation writes one report.
        return result, json.loads(reports[0].read_text())

    return run


@pytest.mark.parametrize("diagnostic", [
    "/bin/sh: 1: uv: not found",
    "sh: 12: uv: not found",
    "check.sh: 27: dependency-tool: not found",
    "check.sh: line 27: dependency-tool: not found",
])
def test_shell_dependency_failure_is_error(monitor, diagnostic):
    # The first diagnostic is the issue's reproduction; other line numbers are
    # synthetic locations, not thresholds. Each fixture has one diagnostic.
    result, report = monitor(diagnostic + "\n")
    assert result.returncode == 1
    assert report["task_count"] == 1
    assert report["healthy"] == 0
    assert report["problems"] == 1
    task, = report["tasks"]
    assert task["status"] == task["log_status"] == "ERROR"
    assert task["errors_found"] == 1
    assert "[ERROR" in result.stdout


@pytest.mark.parametrize("text", [
    "Dependency not found checks completed successfully.\n",
    "Note: optional dependency: not found\nCompleted successfully.\n",
    'Example diagnostic: "/bin/sh: 1: uv: not found"\nCompleted successfully.\n',
    "/bin/sh: 1: uv: not found in optional documentation\nCompleted successfully.\n",
])
def test_successful_log_with_explanatory_text_is_healthy(monitor, text):
    # One scheduled task with no actual failure diagnostic is healthy.
    result, report = monitor(text)
    assert result.returncode == 0
    assert report["task_count"] == report["healthy"] == 1
    assert report["problems"] == 0
    task, = report["tasks"]
    assert task["status"] == task["log_status"] == "OK"
    assert task["errors_found"] == 0
    assert "[OK" in result.stdout


def test_missing_log_stays_missing(monitor):
    # One scheduled task without a log is one problem, with no text matches.
    result, report = monitor(None)
    assert result.returncode == 1
    assert report["task_count"] == report["problems"] == 1
    assert report["healthy"] == 0
    task, = report["tasks"]
    assert task["status"] == task["log_status"] == "MISSING"
    assert task["errors_found"] == 0
    assert task["last_log"] == ""
    assert "[MISSING" in result.stdout
