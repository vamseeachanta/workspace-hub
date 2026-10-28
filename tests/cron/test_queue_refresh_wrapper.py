"""Offline execution tests for the weekly queue wrapper.

Only the wrapper is copied from the repository. Helpers and the no-change
generator are synthetic; no real Git repository or remote is used.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest


WRAPPER = Path(__file__).resolve().parents[2] / "scripts/cron/queue-refresh-weekly.sh"
GENERATOR = "scripts/refresh-agent-work-queue.py"
# Synthetic failure example: a nonzero status distinct from the shell's generic
# failure status. The expected result is this supplied status, unchanged.
GENERATOR_FAILURE = 23
# Python's os interface specifies zero as successful termination.
SUCCESS = os.EX_OK
# Synthetic upper bound for a local shell plus short stub processes, in seconds.
WRAPPER_TIMEOUT = 30


STUB = r'''
import json
import os
from pathlib import Path
import runpy
import sys

name = Path(sys.argv[0]).name
args = sys.argv[1:]
if name == "record":
    name, *args = args
with open(os.environ["CALL_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps([name, args]) + "\n")

if name in {"ws_is", "git_safe_init", "git_safe_pull"}:
    pass
elif name == "uv" and args in (
    ["run", "scripts/refresh-agent-work-queue.py"],
    ["run", "scripts/refresh-agent-work-queue.py", "--dry-run"],
):
    sys.argv = args[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")
elif name == "git" and args == [
    "status", "--porcelain", "--", "notes/agent-work-queue.md"
]:
    pass  # The synthetic generator leaves the queue unchanged.
else:
    raise AssertionError("Forbidden external or mutation call: " + name)
'''

FAKE_GENERATOR = r'''
import json
import os
from pathlib import Path
import sys

with open(os.environ["CALL_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(["generator", sys.argv]) + "\n")
assert Path("notes/agent-work-queue.md").read_text() == "synthetic queue\n"
print("synthetic generator stdout", flush=True)
print("synthetic generator stderr", file=sys.stderr, flush=True)
raise SystemExit(int(os.environ["GENERATOR_STATUS"]))
'''

FAKE_HELPERS = r'''
git_safe_init() { "$STUB_RECORD" git_safe_init "$@"; }
git_safe_pull() { "$STUB_RECORD" git_safe_pull "$@"; }
git_safe_sync() { "$STUB_RECORD" git_safe_sync "$@"; }
git_safe_commit() { "$STUB_RECORD" git_safe_commit "$@"; }
git_safe_push() { "$STUB_RECORD" git_safe_push "$@"; }
'''


@pytest.fixture
def run_wrapper(tmp_path):
    """Run the actual shell wrapper with a closed command search path."""
    root = tmp_path / "copied repository"
    wrapper = root / "scripts/cron/queue-refresh-weekly.sh"
    wrapper.parent.mkdir(parents=True)
    shutil.copyfile(WRAPPER, wrapper)
    helpers = root / "scripts/cron/lib/git-safe.sh"
    helpers.parent.mkdir()
    helpers.write_text(FAKE_HELPERS, encoding="utf-8")
    detection = root / "scripts/lib/workstation-lib.sh"
    detection.parent.mkdir()
    detection.write_text(
        # The wrapper prepends additional command directories at startup.
        # Close the search path again before it reaches any external helper.
        'export PATH="$STUB_BIN"\n'
        'ws_is() { "$STUB_RECORD" ws_is "$@"; }\n', encoding="utf-8"
    )
    (root / GENERATOR).write_text(FAKE_GENERATOR, encoding="utf-8")
    queue = root / "notes/agent-work-queue.md"
    queue.parent.mkdir()
    queue.write_text("synthetic queue\n", encoding="utf-8")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    record = bin_dir / "record"
    record.write_text(f"#!{sys.executable}\n" + STUB, encoding="utf-8")
    record.chmod(record.stat().st_mode | 0o111)  # POSIX execute permission bits.
    for name in (
        "uv", "git", "gh", "curl", "wget", "ssh", "scp", "sftp", "rsync",
        "crontab", "systemctl", "hostname",
    ):
        (bin_dir / name).symlink_to(record)
    # Only these local utilities are reachable. Unlisted commands cannot fall
    # through to the caller's tools; listed remote commands raise in STUB.
    for name in ("date", "dirname", "mkdir", "wc"):
        executable = shutil.which(name)
        assert executable, f"Required local utility unavailable: {name}"
        (bin_dir / name).symlink_to(executable)
    bash = shutil.which("bash")
    assert bash, "Required shell unavailable: bash"
    user_dir = tmp_path / "user"
    user_dir.mkdir()
    calls = tmp_path / "calls.jsonl"
    # Construct a fresh environment, excluding BASH_ENV, inherited Git bindings,
    # provider credentials and user command paths.
    env = {
        "HOME": str(user_dir),
        "PATH": str(bin_dir),
        "TMPDIR": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C",
        "TZ": "UTC",
        "CALL_LOG": str(calls),
        "STUB_RECORD": str(record),
        "STUB_BIN": str(bin_dir),
    }

    def run(*args, generator_status=SUCCESS):
        result = subprocess.run(
            [bash, str(wrapper), *args],
            cwd=tmp_path,
            env={**env, "GENERATOR_STATUS": str(generator_status)},
            capture_output=True,
            text=True,
            timeout=WRAPPER_TIMEOUT,
            check=False,
        )
        trace = [json.loads(line) for line in calls.read_text().splitlines()]
        logs = list((root / "logs/queue-refresh").glob("*.log"))
        # One invocation creates one daily evidence file, named by UTC date.
        (log,) = logs
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}\.log", log.name)
        assert queue.read_text() == "synthetic queue\n"
        assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")
                      if path.is_file()) == sorted([
            wrapper.relative_to(root).as_posix(),
            helpers.relative_to(root).as_posix(),
            detection.relative_to(root).as_posix(),
            GENERATOR,
            queue.relative_to(root).as_posix(),
            log.relative_to(root).as_posix(),
        ])
        assert result.stdout == result.stderr == ""
        return result, trace, log.read_text(), root

    return run


def expected_calls(root, *args, status=False):
    """Contract from the task's synthetic invocation, independent of output."""
    calls = [
        ["ws_is", ["full"]],
        ["git_safe_init", [str(root)]],
        ["git_safe_pull", []],
        ["uv", ["run", GENERATOR, *args]],
        ["generator", [GENERATOR, *args]],
    ]
    if status:
        calls.append(["git", ["status", "--porcelain", "--", "notes/agent-work-queue.md"]])
    return calls


def assert_evidence(log, *messages):
    """Check timestamped evidence and both captured generator streams."""
    lines = log.splitlines()
    wrapper_lines = [line for line in lines if line.startswith("[queue-refresh]")]
    assert [re.sub(r"^\[queue-refresh\] \d{2}:\d{2}:\d{2} ", "", line)
            for line in wrapper_lines] == list(messages)
    assert lines == [
        *wrapper_lines[:2],  # Start and invocation precede generator output.
        "synthetic generator stdout",
        "synthetic generator stderr",
        *wrapper_lines[2:],
    ]


def test_queue_wrapper_forwards_dry_run(run_wrapper):
    result, trace, log, root = run_wrapper("--dry-run")

    assert result.returncode == SUCCESS
    # Exact trace excludes sync and even the normal-mode Git status probe.
    assert trace == expected_calls(root, "--dry-run")
    assert_evidence(
        log,
        "Starting weekly queue refresh",
        f"Running {Path(GENERATOR).name} --dry-run",
        f"Queue refresh completed with exit code {SUCCESS}",
    )


@pytest.mark.parametrize("args", [(), ("--dry-run",)], ids=["normal", "dry-run"])
def test_queue_wrapper_propagates_generator_failure(run_wrapper, args):
    result, trace, log, root = run_wrapper(*args, generator_status=GENERATOR_FAILURE)

    assert result.returncode == GENERATOR_FAILURE
    assert trace == expected_calls(root, *args)
    assert_evidence(
        log,
        "Starting weekly queue refresh",
        f"Running {Path(GENERATOR).name} {' '.join(args)}",
        f"ERROR: {Path(GENERATOR).name} exited with code {GENERATOR_FAILURE}",
    )


def test_queue_wrapper_successful_no_change(run_wrapper):
    result, trace, log, root = run_wrapper()

    assert result.returncode == SUCCESS
    assert trace == expected_calls(root, status=True)
    assert_evidence(
        log,
        "Starting weekly queue refresh",
        f"Running {Path(GENERATOR).name} ",
        "No changes to queue file — skipping commit",
        f"Queue refresh completed with exit code {SUCCESS}",
    )
