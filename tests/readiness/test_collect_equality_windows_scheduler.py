"""Execute the collector's scheduler block without hardware or solver probes.

The CSV syntax and flags follow Microsoft's schtasks query documentation:
https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query
Conversion suppression follows MSYS2 Filesystem Paths, Process Arguments:
https://www.msys2.org/docs/filesystem-paths/
Expected counts are independent enumerations of the synthetic input rows.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

COLLECTOR = Path(__file__).resolve().parents[2] / "scripts/readiness/collect-equality.sh"


def _run(
    tmp_path, output="", *, status=0, available=True, os_name="windows",
    cron_output=None, full_collector=False, write_report=False,
):
    """Source the actual scheduler section; a shim checks argv and its environment."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    if available:
        shim = bin_dir / "schtasks"
        shim.write_text(
            '#!/usr/bin/env bash\n'
            '[[ "${MSYS2_ARG_CONV_EXCL:-}" == "*" ]] || exit 64\n'
            '[[ "$*" == "/query /fo csv /nh" ]] || exit 64\n'
            'printf "%s" "$TASK_OUTPUT"\n'
            'exit "$TASK_STATUS"\n'
        )
        shim.chmod(0o755)
    if cron_output is not None:
        crontab = bin_dir / "crontab"
        crontab.write_text('#!/usr/bin/env bash\nprintf "%s" "$CRON_OUTPUT"\n')
        crontab.chmod(0o755)
    text = COLLECTOR.read_text()
    section = text.split("# ── 8. SCHEDULER", 1)[1].split("# ── 9. PROVENANCE", 1)[0]
    section = section.split("\n", 1)[1]
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "OS": os_name,
        "CRON_OUTPUT": cron_output or "",
        "TASK_OUTPUT": output,
        "TASK_STATUS": str(status),
        "MSYS2_ARG_CONV_EXCL": "inherited-setting",
        "TMPDIR": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    # Missing-command tests must be deterministic even on a native Windows runner.
    have = 'have() { command -v "$1" >/dev/null 2>&1; }\n'
    if not available:
        have = 'have() { return 1; }\n'
    if full_collector:
        # Copy the production entry point without optional hardware/solver helpers.
        # This exercises emission and failure ordering without loading any SDK.
        script = tmp_path / "collect-equality.sh"
        script.write_text(text)
        env.update({
            "WORKSPACE_HUB": str(tmp_path), "HOME": str(tmp_path),
            "EQ_TEST_ENABLE_OS_OVERRIDE": "1", "EQ_OS_OVERRIDE": "windows",
        })
        return subprocess.run(
            ["bash", str(script), "--machine", "fixture"] +
            ([] if write_report else ["--stdout"]),
            env=env, capture_output=True, text=True, check=False,
        )
    return subprocess.run(
        ["bash", "-c", 'set -uo pipefail\n' + have + section +
         '\nprintf "%s %s %s\\n" "$has_sync" "$has_parity" "$job_count"\n'
         'printf "%s\\n" "$MSYS2_ARG_CONV_EXCL"'],
        env=env, capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("task", [
    "RepoSync", "repository-sync", "repo_sync", "EqualityReport", "equality-report",
    "EcosystemReconcile",
])
def test_windows_scheduler_measures_sync_tasks(tmp_path, task):
    r"""One matching row + one unrelated row = two tasks, sync true, parity false.

    PascalCase names come from scripts/windows/setup-scheduler-tasks.ps1;
    separated spellings preserve the cron-style aliases described in the issue.
    """
    result = _run(tmp_path, f'"\\Automation\\{task}","N/A","Ready"\r\n'
                  '"\\Other\\Backup","N/A","Ready"\r\n')
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["true false 2", "inherited-setting"]


def test_windows_scheduler_measures_parity_and_counts_only_csv_rows(tmp_path):
    r"""Two task rows = two; ParityReview sets parity, a status label sets neither."""
    result = _run(tmp_path, '\r\n"\\Automation\\ParityReview","N/A","Ready"\r\n'
                  '"\\Other\\Backup","N/A","RepoSync"\r\n')
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "false true 2"


def test_windows_scheduler_empty_success_is_measured_absence(tmp_path):
    """An empty successful listing contains zero tasks and no matching names."""
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "false false 0"


def test_windows_scheduler_unavailable_stays_unknown(tmp_path):
    """No executable provides no measurement; none of the fields is a boolean."""
    result = _run(tmp_path, available=False)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "unknown unknown unknown"


def test_windows_scheduler_failure_aborts_without_raw_output(tmp_path):
    """Synthetic nonzero exit plus a partial row must never become evidence."""
    result = _run(tmp_path, '"\\Automation\\RepoSync","N/A","Ready"\r\n'
                  'private diagnostic text', status=1)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "schtasks query failed" in result.stderr
    assert "private diagnostic text" not in result.stderr
    assert "RepoSync" not in result.stderr


def test_other_os_does_not_run_windows_query(tmp_path):
    """Without crontab the existing non-Windows defaults remain unchanged."""
    result = _run(tmp_path, available=False, os_name="linux")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "false false 0"


def test_windows_scheduler_large_listing_keeps_early_match(tmp_path):
    r"""One matching row + 4096 filler rows = 4097, irrespective of pipe capacity.

    The synthetic repetition count only forces a listing larger than a pipe buffer;
    the expected total is the independent sum of the rows constructed here.
    """
    output = '"\\Automation\\RepoSync","N/A","Ready"\r\n'
    output += '"\\Other\\Backup","N/A","Ready"\r\n' * 4096
    result = _run(tmp_path, output)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "true false 4097"


def test_linux_crontab_measurement_is_preserved(tmp_path):
    """Two active cron lines after a comment = two jobs, both booleans true."""
    result = _run(tmp_path, os_name="linux", cron_output=(
        "# synthetic schedule\n* * * * * repo-sync\n* * * * * parity-review\n"))
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "true true 2"


def test_full_collector_emits_worked_example(tmp_path):
    r"""Three quoted rows, two sync aliases, no parity alias => true, false, three.

    This is the independent enumeration in docs/readiness-windows-scheduler.md.
    """
    rows = ["EqualityReport", "SessionCuration", "EcosystemReconcile"]
    output = "".join(f'"\\Automation\\{name}","N/A","Ready"\r\n' for name in rows)
    result = _run(tmp_path, output, full_collector=True)
    assert result.returncode == 0, result.stderr
    assert "  scheduler:\n    has_repo_sync: true\n" in result.stdout
    assert "    has_parity_review: false\n    job_count: 3\n" in result.stdout


def test_full_collector_failure_preserves_prior_report(tmp_path):
    """A failed query produces no stdout and leaves the prior evidence byte-for-byte."""
    prior = tmp_path / ".claude/state/equality-fixture.yaml"
    prior.parent.mkdir(parents=True)
    original = b"scheduler: {has_repo_sync: true}\n"
    prior.write_bytes(original)
    result = _run(
        tmp_path, "private diagnostic text", status=1,
        full_collector=True, write_report=True,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "schtasks query failed" in result.stderr
    assert "private diagnostic text" not in result.stderr
    assert prior.read_bytes() == original
