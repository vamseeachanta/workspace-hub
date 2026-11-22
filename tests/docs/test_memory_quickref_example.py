"""Execute the scratch-only example required by issues/1919."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]  # tests/docs is two levels below root.
REFERENCE = ROOT / "docs/plans/memory-ecosystem-quickref.md"
REPORTER = Path("scripts/cron/memory-health-report.sh")
COMMON = Path("scripts/cron/lib/cadence-common.sh")


def _report_tree(root):
    """Record names and metadata, including directories, without writing there."""
    return {
        str(path.relative_to(root)): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in root.rglob("*")
    }


@pytest.fixture
def isolated_reporter(tmp_path):
    """Copy only the real reporter and its dependency into a disposable root."""
    repo = tmp_path / "fixture repository"
    for relative in (REPORTER, COMMON):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return repo


@pytest.fixture
def scratch_environment(tmp_path):
    """Allow local utilities only; record and reject external actions."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for command in (
        "bash", "dirname", "mktemp", "mkdir", "find", "stat", "awk", "wc",
        "tr", "sort", "head", "date", "grep", "cat", "rm",
    ):
        executable = shutil.which(command)
        assert executable, f"required local utility missing: {command}"
        (bindir / command).symlink_to(executable)
    identity = bindir / "hostname"
    identity.write_text("#!/bin/bash\nprintf '%s\\n' fixture\n", encoding="utf-8")
    identity.chmod(0o755)  # POSIX executable script permissions.
    denied = tmp_path / "external-actions"
    for command in ("git", "curl", "wget", "ssh", "systemctl", "crontab"):
        stub = bindir / command
        stub.write_text(
            '#!/bin/bash\nprintf "%s\\n" "$0" >> "$DENIED_ACTIONS"\nexit 1\n',
            encoding="utf-8",
        )
        stub.chmod(0o755)  # POSIX executable script permissions.
    scratch = tmp_path / "scratch space"
    scratch.mkdir()
    home = tmp_path / "empty-user-directory"
    home.mkdir()
    # An explicit environment excludes inherited Git bindings and shell startup hooks.
    return {
        "PATH": str(bindir), "HOME": str(home), "TMPDIR": str(scratch),
        "DENIED_ACTIONS": str(denied), "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",  # Python's documented no-bytecode switch.
    }


def test_memory_quickref_example_runs_in_scratch(isolated_reporter, scratch_environment):
    text = REFERENCE.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 100  # issues/1919 quick-reference line limit.
    section = text.split("## Scratch-only health report\n")
    assert len(section) == 2, "missing unique scratch example"  # Before + after heading.
    blocks = re.findall(r"^```bash\n(.*?)^```$", section[-1], flags=re.M | re.S)
    assert len(blocks) == 1  # issues/1919 requests one executable example.
    reports = ROOT / "docs/reports"
    before = _report_tree(reports)
    try:
        result = subprocess.run(
            [str(Path(scratch_environment["PATH"]) / "bash"), "-c", blocks[0]],
            cwd=isolated_reporter,
            env=scratch_environment,
            capture_output=True,
            text=True,
            timeout=30,  # Twice tests/cron/test_memory_health_report.py's 15s budget.
        )
    finally:
        assert _report_tree(reports) == before, "repository reports changed"
        assert not (isolated_reporter / "docs/reports").exists()
    assert result.returncode == 0, result.stderr  # POSIX successful command status.
    assert not Path(scratch_environment["DENIED_ACTIONS"]).exists()
    scratch = Path(scratch_environment["TMPDIR"])
    generated = list(scratch.glob("memory-health-example.*/reports/*.md"))
    assert len(generated) == 1  # One invocation in the documented example.
    report = generated.pop()
    assert report.name == "memory-health-2026-W16.md"  # Reporter's fixture period.
    body = report.read_text(encoding="utf-8")
    assert "synthetic-topic.md" in body  # Literal input filename in the example.
    assert "synthetic-topic.md" in result.stdout  # The example inspects the report.
    assert str(scratch) in body
    assert "Status:** GREEN" in body  # One short topic is below the documented 5 MB.
    assert "across 1 files" in body  # Hand count: the example creates one memory file.
    inputs = list(scratch.glob("memory-health-example.*/memory/*.md"))
    assert len(inputs) == 1  # Same hand count; no real memory directories are copied.
    assert inputs.pop().read_text(encoding="utf-8") == (
        "Synthetic topic for the health report.\n"  # Literal example input.
    )
    assert not any(Path(scratch_environment["HOME"]).iterdir())
