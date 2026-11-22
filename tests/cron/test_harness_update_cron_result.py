"""Isolated sync_crontab result contract for issue #3479.

Status 0 denotes shell success; 7 is a synthetic nonzero fixture status.
Fixture schedule text is synthetic: two matching lines imply a count of two
by direct enumeration, independent of the helper's output-counting code.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest


# Two parent directories separate this test folder from the repository root.
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/cron/harness-update.sh"
SUCCESS = 0
FAILURE = 7
SCHEDULE_PREVIEW = "Preview:\n  * synthetic-entry-a\n  * synthetic-entry-b\n"
APPLY_SUCCESS = "Installed synthetic entries\n"
DIAGNOSTIC = "synthetic installer refusal; inspect reconciliation inputs"


def _sync_definition() -> str:
    source = SCRIPT.read_text(encoding="utf-8")
    definitions = re.findall(r"^sync_crontab\(\) \{\n.*?^\}", source, re.M | re.S)
    assert len(definitions) == 1, "extract exactly one tracked function definition"
    assert len(re.findall(r"^sync_crontab\s*\(\)", source, re.M)) == 1
    return definitions[0]


def _run_sync(
    root: Path,
    *,
    dry_run: bool,
    status: int = SUCCESS,
    stdout: str = "",
    stderr: str = "",
    present: bool = True,
) -> subprocess.CompletedProcess[str]:
    cron_dir = root / "scripts/cron"
    cron_dir.mkdir(parents=True)
    command_log = root / "installer-commands.txt"
    command_log.write_text("", encoding="utf-8", newline="\n")
    if present:
        (cron_dir / "setup-cron.sh").write_text(
            'printf "installer" >> "$COMMAND_LOG"\n'
            'for arg in "$@"; do printf " <%s>" "$arg" >> "$COMMAND_LOG"; done\n'
            'printf "\\n" >> "$COMMAND_LOG"\n'
            'printf "%s" "$INSTALLER_STDOUT"\n'
            'printf "%s" "$INSTALLER_STDERR" >&2\n'
            'exit "$INSTALLER_STATUS"\n',
            encoding="utf-8", newline="\n",
        )

    # Any scheduler call is intercepted; neither state nor unrelated files may change.
    scheduler = root / "scheduler-state.txt"
    sentinel = root / "sentinel.txt"
    scheduler.write_bytes(b"synthetic scheduler state\n")
    sentinel.write_bytes(b"unrelated sentinel\n")
    protected = {path: path.read_bytes() for path in (scheduler, sentinel)}
    bin_dir = root / "bin"
    bin_dir.mkdir()
    scheduler_command = bin_dir / "crontab"
    scheduler_command.write_text(
        '#!/usr/bin/env bash\nprintf "unexpected scheduler call" > "$SCHEDULER_STATE"\n',
        encoding="utf-8", newline="\n",
    )
    scheduler_command.chmod(scheduler_command.stat().st_mode | 0o111)
    # Use only fixture inputs and system tools, without inherited repository bindings.
    env = {
        "PATH": f"{bin_dir}:{os.defpath}",
        "WORKSPACE_HUB": str(root),
        "DRY_RUN": str(dry_run).lower(),
        "COMMAND_LOG": str(command_log),
        "SCHEDULER_STATE": str(scheduler),
        "INSTALLER_STATUS": str(status),
        "INSTALLER_STDOUT": stdout,
        "INSTALLER_STDERR": stderr,
    }
    result = subprocess.run(
        [
            "bash",
            "-c",
            "set -uo pipefail\n"
            'log() { printf "%s\\n" "$*"; }\n'
            + _sync_definition()
            + '\nsync_crontab\nstatus=$?\nprintf "update continues\\n"\nexit "$status"\n',
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        # Match the existing setup-cron subprocess timeout (seconds).
        timeout=30,
    )
    assert {path: path.read_bytes() for path in protected} == protected
    expected_command = "installer <--dry-run>\n" if dry_run else "installer\n"
    assert command_log.read_text(encoding="utf-8") == (expected_command if present else "")
    print(f"fixture command: {expected_command.strip() if present else 'absent; no invocation'}")
    print(f"fixture result: status={result.returncode}; {result.stdout.strip()}")
    return result


def test_dry_run_success_counts_fixture_entries(tmp_path):
    result = _run_sync(tmp_path, dry_run=True, stdout=SCHEDULE_PREVIEW)

    assert result.returncode == SUCCESS
    assert "dry-run: 2 schedule-tasks.yaml entry/entries would be ensured" in result.stdout
    assert "failed" not in result.stdout
    assert result.stderr == ""


def test_dry_run_installer_failure_is_not_reported_as_zero_work(tmp_path):
    result = _run_sync(tmp_path, dry_run=True, status=FAILURE, stderr=DIAGNOSTIC)

    assert "dry-run failed" in result.stdout
    assert f"exit {FAILURE}" in result.stdout
    assert DIAGNOSTIC in result.stdout
    assert "inspect" in result.stdout
    assert "would be ensured" not in result.stdout


def test_apply_success_preserves_installer_summary(tmp_path):
    result = _run_sync(tmp_path, dry_run=False, stdout=APPLY_SUCCESS)

    assert result.returncode == SUCCESS
    assert "CRON Installed synthetic entries" in result.stdout
    assert "failed" not in result.stdout
    assert result.stderr == ""


def test_apply_failure_logs_status_even_with_success_looking_stdout(tmp_path):
    result = _run_sync(
        tmp_path, dry_run=False, status=FAILURE, stdout=APPLY_SUCCESS, stderr=DIAGNOSTIC
    )

    assert "apply failed" in result.stdout
    assert f"exit {FAILURE}" in result.stdout
    assert DIAGNOSTIC in result.stdout
    assert "inspect" in result.stdout
    assert "CRON Installed synthetic entries" not in result.stdout


@pytest.mark.parametrize("dry_run", [True, False])
def test_success_and_missing_installer_have_distinct_messages(tmp_path, dry_run):
    success = _run_sync(
        tmp_path / "success", dry_run=dry_run,
        stdout=SCHEDULE_PREVIEW if dry_run else APPLY_SUCCESS,
    )
    missing = _run_sync(tmp_path / "missing", dry_run=dry_run, present=False)

    assert success.returncode == missing.returncode == SUCCESS
    assert "setup-cron.sh absent — skip" in missing.stdout
    assert "absent" not in success.stdout
    assert "would be ensured" not in missing.stdout
    assert "Installed" not in missing.stdout
    assert "failed" not in missing.stdout


@pytest.mark.parametrize("dry_run", [True, False])
def test_cron_failure_preserves_documented_nonfatal_contract(tmp_path, dry_run):
    result = _run_sync(tmp_path, dry_run=dry_run, status=FAILURE, stderr=DIAGNOSTIC)

    assert result.returncode == SUCCESS
    assert "update continues" in result.stdout
    assert "failures are logged only" in SCRIPT.read_text(encoding="utf-8")
