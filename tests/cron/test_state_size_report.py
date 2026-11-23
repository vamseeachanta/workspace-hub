"""Tests for scripts/cron/state-size-report.sh — TDD per #2070 plan."""

import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "state-size-report.sh"

# Existing report contract: scripts/cron/state-size-report.sh, Env overrides
# and integer MB conversion. One MiB is 2**20 bytes; defaults are 50/75 MiB.
# Band comparisons follow scripts/cron/lib/cadence-common.sh, Threshold semantics.
MIB = 1024 * 1024
DEFAULT_WARN_MB = 50
DEFAULT_BLOCK_MB = 75
# Monday 2026-04-13 is in week 16 (counting from Monday 2025-12-29).
REPORT_WEEK = "2026-W16"


def _git_env() -> dict[str, str]:
    """Keep fixture Git commands independent of caller repository bindings."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _make_repo_with_state_files(tmp_path: Path, files: dict[str, int]) -> Path:
    """Track empty files, then set sparse working-tree sizes in MiB."""
    repo = tmp_path / "repo with spaces"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "-q", "-b", "main"], cwd=repo, env=_git_env(), check=True,
    )
    for rel, mb in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        subprocess.run(["git", "add", rel], cwd=repo, env=_git_env(), check=True)
        with p.open("wb") as f:
            f.truncate(mb * MIB)
    return repo


def _run(
    repo: Path, env_extra: dict | None = None, *, cwd: Path | None = None,
) -> tuple[subprocess.CompletedProcess, Path]:
    out_dir = repo / "out"
    env = _git_env()
    for name in (
        "REPO_ROOT", "STATE_REPORT_REPO_ROOT", "STATE_REPORT_OUT_DIR",
        "STATE_REPORT_WEEK", "STATE_SIZE_WARN_MB", "STATE_SIZE_BLOCK_MB",
    ):
        env.pop(name, None)
    env["STATE_REPORT_REPO_ROOT"] = str(repo)
    env["STATE_REPORT_OUT_DIR"] = str(out_dir)
    env["STATE_REPORT_WEEK"] = REPORT_WEEK
    for name, value in (env_extra or {}).items():
        if value is None:
            env.pop(name, None)
        else:
            env[name] = value
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=cwd or repo, env=env, capture_output=True, text=True, timeout=30,
    )
    selected_dir = Path(env.get("STATE_REPORT_OUT_DIR", repo / "docs" / "reports"))
    return r, selected_dir / f"state-size-{env.get('STATE_REPORT_WEEK', REPORT_WEEK)}.md"


def test_size_report_lists_top_10(tmp_path):
    """Plan acceptance: report contains a top-10 markdown table."""
    files = {f".claude/state/session-signals/file{i:02d}.jsonl": i for i in range(1, 12)}
    repo = _make_repo_with_state_files(tmp_path, files)
    r, report = _run(repo)
    assert r.returncode == 0, r.stderr
    assert report.is_file()
    body = report.read_text()
    assert "## Top 10 largest tracked files" in body
    # Existing report contract: head -10 after descending numeric size sort.
    table = body.split("## Top 10 largest tracked files", 1)[1].split("## Source", 1)[0]
    rows = [ln for ln in table.splitlines() if ln.startswith("| ") and "Size (MB)" not in ln and "----" not in ln]
    assert len(rows) == 10
    assert [int(row.split("|")[1]) for row in rows] == list(range(11, 1, -1))
    assert "file01.jsonl" not in table


def test_size_report_status_green_when_all_small(tmp_path):
    repo = _make_repo_with_state_files(
        tmp_path, {".claude/state/session-signals/small.jsonl": 5}
    )
    r, report = _run(repo)
    assert r.returncode == 0
    assert "Status:** GREEN" in report.read_text()


def test_size_report_status_yellow_when_warn(tmp_path):
    repo = _make_repo_with_state_files(
        tmp_path, {".claude/state/session-signals/mid.jsonl": 60}
    )
    r, report = _run(repo)
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** YELLOW" in body
    assert "over warn" in body


def test_size_report_status_red_when_over_block(tmp_path):
    repo = _make_repo_with_state_files(
        tmp_path, {".claude/state/session-signals/huge.jsonl": 80}
    )
    r, report = _run(repo)
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** RED" in body
    assert "OVER BLOCK" in body


def test_size_report_handles_empty_state_dir(tmp_path):
    """No tracked state files → still produce a report with totals=0, status GREEN."""
    repo = _make_repo_with_state_files(tmp_path, {"README.md": 0})
    untracked = repo / ".claude" / "state" / "untracked.jsonl"
    untracked.parent.mkdir(parents=True)
    with untracked.open("wb") as f:
        f.truncate((DEFAULT_BLOCK_MB + 1) * MIB)
    r, report = _run(repo)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body
    assert "0 files, 0MB." in body
    assert "largest tracked file is 0MB" in body
    assert "untracked.jsonl" not in body
    assert not any(line.startswith("| 0 |") for line in body.splitlines())


@pytest.mark.parametrize("overrides,warn,block", [
    ({}, DEFAULT_WARN_MB, DEFAULT_BLOCK_MB),
    # Synthetic override examples: vary each threshold alone and both together.
    ({"STATE_SIZE_WARN_MB": "5"}, 5, DEFAULT_BLOCK_MB),
    ({"STATE_SIZE_BLOCK_MB": "100"}, DEFAULT_WARN_MB, 100),
    ({"STATE_SIZE_WARN_MB": "2", "STATE_SIZE_BLOCK_MB": "4"}, 2, 4),
])
@pytest.mark.parametrize("boundary", ["warn", "block"])
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_size_report_strict_boundaries(tmp_path, overrides, warn, block, boundary, offset):
    """Independently compare one MiB below, equal to, and above each limit."""
    mb = (warn if boundary == "warn" else block) + offset
    path = ".claude/state/sample with spaces.jsonl"
    repo = _make_repo_with_state_files(tmp_path, {path: mb})
    r, report = _run(repo, overrides)
    assert r.returncode == 0, r.stderr
    # Direct comparisons from the cited helper contract, never helper output.
    expected = "RED" if mb > block else "YELLOW" if mb > warn else "GREEN"
    flag = "🔴 OVER BLOCK" if mb > block else "🟡 over warn" if mb > warn else ""
    assert report.read_text() == (
        f"# State-file size report — {REPORT_WEEK}\n\n"
        f"**Status:** {expected} — largest tracked file is {mb}MB "
        f"(warn {warn}MB, block {block}MB).\n\n"
        f"Total tracked under .claude/state/: 1 files, {mb}MB.\n\n"
        "## Top 10 largest tracked files\n\n"
        "| Size (MB) | Path | Flag |\n"
        "|-----------|------|------|\n"
        f"| {mb} | `{path}` | {flag} |\n\n"
        "## Source\n\n"
        "Generated by `scripts/cron/state-size-report.sh` (#2070).\n"
    )
    assert f"wrote {report} (status: {expected})" in r.stdout


@pytest.mark.parametrize("mb", [DEFAULT_WARN_MB, DEFAULT_BLOCK_MB])
def test_size_report_truncates_before_comparing(tmp_path, mb):
    """One byte below the next MiB still has the boundary's original band."""
    path = ".claude/state/fractional.jsonl"
    repo = _make_repo_with_state_files(tmp_path, {path: mb})
    with (repo / path).open("r+b") as f:
        f.truncate((mb + 1) * MIB - 1)
    r, report = _run(repo)
    assert r.returncode == 0, r.stderr
    expected = "YELLOW" if mb > DEFAULT_WARN_MB else "GREEN"
    assert f"**Status:** {expected}" in report.read_text()
    assert f"largest tracked file is {mb}MB" in report.read_text()


def test_size_report_explicit_destinations_from_other_directory(tmp_path):
    path = ".claude/state/selected.jsonl"
    repo = _make_repo_with_state_files(tmp_path, {path: DEFAULT_WARN_MB})
    caller = tmp_path / "caller"
    caller.mkdir()
    destination = tmp_path / "selected output"
    # Synthetic filename override; week 17 follows the fixed week-16 example.
    week = "2026-W17"
    r, report = _run(repo, {
        "STATE_REPORT_OUT_DIR": str(destination), "STATE_REPORT_WEEK": week,
        "REPO_ROOT": str(caller),
    }, cwd=caller)
    assert r.returncode == 0, r.stderr
    assert report == destination / f"state-size-{week}.md"
    body = report.read_text()
    assert body.startswith(f"# State-file size report — {week}\n")
    assert f"1 files, {DEFAULT_WARN_MB}MB." in body
    assert f"`{path}`" in body
    assert f"wrote {report}" in r.stdout
    assert list(destination.iterdir()) == [report]
    assert not (repo / "out").exists()
    assert not (caller / "docs").exists()


@pytest.mark.parametrize("root_override", [None, ""])
def test_size_report_git_root_and_default_output(tmp_path, root_override):
    repo = _make_repo_with_state_files(tmp_path, {})
    nested = repo / "nested directory"
    nested.mkdir()
    r, report = _run(repo, {
        "STATE_REPORT_REPO_ROOT": root_override, "STATE_REPORT_OUT_DIR": None,
        "REPO_ROOT": str(tmp_path),
    }, cwd=nested)
    assert r.returncode == 0, r.stderr
    assert report == repo / "docs" / "reports" / f"state-size-{REPORT_WEEK}.md"
    assert report.is_file()
    assert not (nested / "docs").exists()


def test_size_report_pwd_root_fallback(tmp_path):
    """Outside Git, the report uses the calling directory."""
    repo = tmp_path / "not a repository"
    repo.mkdir()
    r, report = _run(repo, {"STATE_REPORT_REPO_ROOT": None})
    assert r.returncode == 0, r.stderr
    assert "0 files, 0MB." in report.read_text()


@pytest.mark.parametrize("fixed_date,expected_week", [
    ("2026-04-13 12:00:00 UTC", "2026-W16"),
    # The existing date contract uses calendar year %Y and ISO week %V:
    # Friday 2021-01-01 belongs to the week starting Monday 2020-12-28, week 53.
    ("2021-01-01 12:00:00 UTC", "2021-W53"),
])
def test_size_report_default_week_from_fixed_date(tmp_path, fixed_date, expected_week):
    repo = _make_repo_with_state_files(tmp_path, {})
    tools = tmp_path / "tools"
    tools.mkdir()
    # Reject native date delegation, including GNU-only --date clock injection.
    real_date = tools / "system-date"
    real_date.write_text("#!/usr/bin/env bash\nexit 99\n")
    real_date.chmod(0o755)
    date = tools / "date"
    # Use Python calendar arithmetic so neither GNU nor BSD date is required.
    # Check the requested format and UTC rather than masking a helper regression.
    date.write_text(
        f"#!/usr/bin/env bash\nexec {shlex.quote(sys.executable)} - \"$@\" <<'PY'\n"
        "import os\n"
        "import sys\n"
        "from datetime import datetime\n"
        "assert sys.argv[1:] == ['+%Y-W%V'], sys.argv[1:]\n"
        "assert os.environ['TZ'] == 'UTC'\n"
        "clock = datetime.strptime(os.environ['FIXED_DATE'], '%Y-%m-%d %H:%M:%S UTC')\n"
        "print(f'{clock.year:04d}-W{clock.isocalendar().week:02d}')\n"
        "PY\n"
    )
    date.chmod(0o755)
    r, _ = _run(repo, {
        "STATE_REPORT_WEEK": None, "TZ": "UTC", "FIXED_DATE": fixed_date,
        "REAL_DATE": str(real_date),
        "PATH": str(tools) + os.pathsep + os.environ["PATH"],
    })
    report = repo / "out" / f"state-size-{expected_week}.md"
    assert r.returncode == 0, r.stderr
    assert report.read_text().startswith(f"# State-file size report — {expected_week}\n")
    assert list((repo / "out").iterdir()) == [report]
