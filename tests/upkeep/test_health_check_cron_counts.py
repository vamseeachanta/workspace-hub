"""Execute the terminal report against synthetic cron data, without host probes.

Independent synthetic hand calculation: two jobs with counters two and three
have five historical completions (2 + 3 = 5), regardless of current state.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest


REPORT = Path(__file__).resolve().parents[2] / "scripts/upkeep/health-check.sh"


@pytest.fixture
def run_report(tmp_path, request):
    root = tmp_path / getattr(request, "param", "report fixture")
    root.mkdir()
    cron = root / ".hermes/cron"
    cron.mkdir(parents=True)
    (cron / "output").write_text("synthetic output\n")
    memories = root / ".hermes/memories"
    memories.mkdir()
    for name in ("MEMORY.md", "USER.md"):
        (memories / name).write_text("synthetic memory\n")
    topics = root / ".claude/memory/topics"
    topics.mkdir(parents=True)
    (topics / "fixture.md").write_text("synthetic topic\n")
    (topics.parent / "claude-auto-memory.md").write_text("synthetic snapshot\n")

    bin_dir = root / "bin"
    bin_dir.mkdir()
    # All unrelated service, repository, time and filesystem probes are stubs.
    # Zero percent below represents an empty synthetic disk, not a host reading.
    stub = """#!/usr/bin/env bash
set -eu
name="${0##*/}"
printf '%s\\n' "$name" >> "$PROBE_LOG"
case "$name" in
    systemctl)
        case "$1" in
            is-active) echo active ;;
            show) echo ActiveEnterTimestamp=synthetic ;;
            *) exit 99 ;;
        esac ;;
    git)
        case "$*" in
            'rev-parse --show-toplevel') echo "$FIXTURE_ROOT" ;;
            *'log -1 --format=%ct'*) echo "$FIXTURE_EPOCH" ;;
            *'log --oneline origin/main..main') : ;;
            *) exit 99 ;;
        esac ;;
    date)
        case "$1" in
            +%s) echo "$FIXTURE_EPOCH" ;;
            +%Y-%m-%d) echo synthetic-date ;;
            *) exit 99 ;;
        esac ;;
    df) echo 'fixture 100 0 100 0% fixture' ;;
    du) echo '0 fixture' ;;
    find) echo "$FIXTURE_ROOT/.claude/memory/topics/fixture.md" ;;
    stat) echo "$FIXTURE_EPOCH" ;;
    *) exit 99 ;;
esac
"""
    for name in ("systemctl", "git", "date", "df", "du", "find", "stat"):
        command = bin_dir / name
        command.write_text(stub)
        command.chmod(0o755)
    (bin_dir / "python3").symlink_to(sys.executable)
    probe_log = root / "probes.log"
    env = {
        "HOME": str(root),
        "PATH": str(bin_dir) + os.pathsep + os.defpath,
        "FIXTURE_ROOT": str(root),
        "FIXTURE_EPOCH": str(int(time.time())),
        "PROBE_LOG": str(probe_log),
        "PYTHONDONTWRITEBYTECODE": "1",
        "TMPDIR": str(tmp_path),
    }

    def run(payload):
        (cron / "jobs.json").write_text(payload)
        result = subprocess.run(
            [shutil.which("bash"), str(REPORT)],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,  # Bound a fixture-only report; no service waits are needed.
        )
        assert result.stderr == ""
        assert "Ecosystem Health" in result.stdout
        assert "Total:" in result.stdout
        assert set(probe_log.read_text().splitlines()) == {
            "systemctl", "git", "date", "df", "du", "find", "stat"
        }
        assert not (root / "logs").exists()  # Terminal mode never saves a report.
        return result

    return run


def assert_counts(result, jobs, completions):
    # Exit zero establishes that unrelated fixture checks stayed healthy.
    assert result.returncode == 0, result.stdout
    row = next(line for line in result.stdout.splitlines() if "Cron (" in line)
    assert f"Cron ({jobs} jobs)" in row
    assert "✅" in row
    assert f"{completions} total completions" in row
    assert "scheduled" not in row


def test_scheduled_jobs_retain_historical_completions(run_report):
    jobs = [
        {"state": "scheduled", "repeat": {"completed": 2}},
        {"state": "scheduled", "repeat": {"completed": 3}},
    ]
    assert_counts(run_report(json.dumps(jobs)), jobs=2, completions=5)


def test_mixed_states_do_not_determine_counts(run_report):
    # Hand calculation: three entries, 2 + 3 + 0 = 5 completions.
    jobs = [
        {"state": "running", "repeat": {"completed": 2}},
        {"state": "completed", "repeat": {"completed": 3}},
        {"state": "failed", "repeat": {"completed": 0}},
    ]
    assert_counts(run_report(json.dumps(jobs)), jobs=3, completions=5)


def test_missing_repeat_defaults_to_zero(run_report):
    # Hand calculation: three entries, absent + absent + 2 = 0 + 0 + 2.
    jobs = [{}, {"repeat": {}}, {"repeat": {"completed": 2}}]
    assert_counts(run_report(json.dumps(jobs)), jobs=3, completions=2)


def test_empty_array_is_healthy_zero(run_report):
    # The empty array has zero entries and its empty sum is zero.
    assert_counts(run_report("[]"), jobs=0, completions=0)


@pytest.mark.parametrize("run_report", ["report's fixture"], indirect=True)
def test_json_path_is_passed_without_code_interpolation(run_report):
    # Same empty-array oracle, with a quote and spaces in the fixture path.
    assert_counts(run_report("[]"), jobs=0, completions=0)


@pytest.mark.parametrize("payload", ["", " ", "[{", "[] trailing"])
def test_malformed_jobs_is_not_healthy_zero(run_report, payload):
    assert_unavailable(run_report(payload))


@pytest.mark.parametrize(
    "payload",
    [
        "null", "{}", '{"jobs": []}', '"jobs"', "[null]", "[[]]",
        '[{"repeat": null}]', '[{"repeat": []}]',
        '[{"repeat": {"completed": -1}}]',
        '[{"repeat": {"completed": true}}]',
        '[{"repeat": {"completed": 2.5}}]',
        '[{"repeat": {"completed": "3"}}]',
        '[{"repeat": {"completed": null}}]',
        # A valid earlier entry must not hide a later invalid counter.
        '[{"repeat": {"completed": 2}}, {"repeat": {"completed": -1}}]',
    ],
)
def test_unsupported_jobs_are_unavailable(run_report, payload):
    # Negative, boolean, fractional, string and null values are not counters.
    assert_unavailable(run_report(payload))


def assert_unavailable(result):
    # The existing report contract assigns exit one to warnings only.
    assert result.returncode == 1, result.stdout
    row = next(line for line in result.stdout.splitlines() if "Cron (" in line)
    assert "Cron (unavailable)" in row
    assert "⚠️" in row
    assert "0 jobs" not in row
    assert "total completions" not in row
