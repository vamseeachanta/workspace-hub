"""Offline argv contract for the publisher's sparse-checkout boundary.

Expected tokens are transcribed from scripts/readiness/publish-equality.sh,
attempt(), at the sparse-checkout call. This tests argument construction only;
the conversion below is deliberately synthetic, not native MSYS behavior.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Root traversal and subprocess timeout follow test_publish_equality.py's harness.
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/readiness/publish-equality.sh"
TIMEOUT = 120
# Independent literal oracle: publish-equality.sh, attempt(), sparse-checkout set.
SPARSE_ARGS = [
    "sparse-checkout", "set", "--no-cone",
    ".claude/state/", "docs/reports/", "scripts/readiness/",
]

# No subprocess or real Git fallback exists in this executable. Only the exact
# bootstrap calls needed to reach sparse-checkout receive canned success; even
# fetch and worktree setup/cleanup are inert. Everything else fails closed.
GIT_STUB = r'''
import json
import os
import sys

raw = sys.argv[1:]
converted = [
    "converted:" + token if token.startswith("/") else token
    for token in raw
] if os.environ["SIMULATE_CONVERSION"] == "yes" else raw
# Git's -C takes one operand; only the following tokens select the command.
command = raw[2:] if raw[:1] == ["-C"] else raw
repo = os.environ["FIXTURE_REPO"]
wt_root = os.environ["TMPDIR"] + os.sep
kind = "forbidden"
if raw == ["-C", os.environ["SCRIPT_DIRECTORY"], "rev-parse", "--show-toplevel"]:
    kind = "bootstrap"
elif raw == ["-C", repo, "fetch", "origin", "main", "--quiet"]:
    kind = "bootstrap"
elif raw == ["-C", repo, "worktree", "prune"]:
    kind = "bootstrap"
elif raw[:2] == ["-C", repo] and command[:1] == ["worktree"]:
    if command[:4] == ["worktree", "add", "--no-checkout", "--detach"]:
        if len(command) == 6 and command[4].startswith(wt_root) and command[5] == "origin/main":
            kind = "bootstrap"
    elif command[:3] == ["worktree", "remove", "--force"]:
        if len(command) == 4 and command[3].startswith(wt_root):
            kind = "bootstrap"
elif raw[:1] == ["-C"] and raw[1].startswith(wt_root) and command[:1] == ["sparse-checkout"]:
    kind = "stop"
with open(os.environ["ARGV_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps({"raw": raw, "converted": converted, "kind": kind}) + "\n")
if kind == "bootstrap":
    if command == ["rev-parse", "--show-toplevel"]:
        print(repo)
    sys.exit(0)
# Bash false uses status 1: deliberate stop and forbidden operations both fail.
sys.exit(1)
'''


@pytest.fixture(params=["working", "working directory with spaces"])
def probe(tmp_path, request):
    """Run the unmodified script with synthetic evidence and an inert Git stub."""
    root = tmp_path / request.param
    root.mkdir()
    repo = root / "repository"
    repo.mkdir()
    state = root / "evidence"
    state.mkdir()
    # Only existence is inspected before sparse-checkout; no evidence is copied.
    (state / "equality-test.yaml").write_text("", encoding="utf-8")
    temp = root / "temporary files"
    temp.mkdir()
    bindir = root / "bin"
    bindir.mkdir()
    git = bindir / "git"
    git.write_text(f"#!{sys.executable}\n" + GIT_STUB, encoding="utf-8")
    # Permission bits: user rwx (7), group rx (5), others rx (5).
    git.chmod(0o755)
    # Do not query the real host, read identity files or invoke notification code.
    hostname = bindir / "hostname"
    hostname.write_text("#!/bin/sh\nprintf '%s\\n' test\n", encoding="utf-8")
    hostname.chmod(0o755)
    log = root / "argv.jsonl"
    # An allowlisted environment excludes inherited Git bindings, shell startup
    # files and functions. Utilities use the system path; Git always hits the stub.
    env = {
        "PATH": os.pathsep.join((str(bindir), os.defpath)),
        "HOME": str(root),
        "TMPDIR": str(temp),
        "PYTHONDONTWRITEBYTECODE": "1",
        "EQ_MACHINE": "test",
        "EQ_STATE_DIR": str(state),
        "FIXTURE_REPO": str(repo),
        "SCRIPT_DIRECTORY": str(SCRIPT.parent),
        "ARGV_LOG": str(log),
    }
    assert shutil.which("git", path=env["PATH"]) == str(git)

    def run(simulate=False):
        child_env = {**env, "SIMULATE_CONVERSION": "yes" if simulate else "no"}
        result = subprocess.run(
            ["bash", str(SCRIPT), "--repo", str(repo),
             "--max-attempts", "1", "--retry-delay-seconds", "0"],
            cwd=root, env=child_env, capture_output=True, text=True, timeout=TIMEOUT,
        )
        # One attempt, no delay: deliberately fail at sparse-checkout, then exit.
        assert result.returncode == 1, result
        assert "could not publish" in result.stderr
        records = [json.loads(line) for line in log.read_text().splitlines()]
        assert [record["kind"] for record in records] == [
            "bootstrap", "bootstrap", "bootstrap", "bootstrap",
            "stop", "bootstrap", "bootstrap",
        ]
        # This exact trace excludes remote configuration, checkout, staging,
        # commits, pushes and every other unexpected Git mutation.
        commands = [record["raw"][2:] for record in records]
        _, _, _, add, _, _, _ = commands
        _, _, _, _, worktree, _ = add
        assert Path(worktree).parent == temp
        assert commands == [
            ["rev-parse", "--show-toplevel"], ["worktree", "prune"],
            ["fetch", "origin", "main", "--quiet"],
            ["worktree", "add", "--no-checkout", "--detach", worktree, "origin/main"],
            SPARSE_ARGS,
            ["worktree", "remove", "--force", worktree], ["worktree", "prune"],
        ]
        # The stub never creates a worktree or any files in the synthetic repo.
        assert not Path(worktree).exists()
        assert not list(repo.iterdir())
        stopped, = (record for record in records if record["kind"] == "stop")
        assert stopped["raw"] == ["-C", worktree, *SPARSE_ARGS]
        return stopped, child_env, git, log, worktree

    return run


def test_sparse_patterns_are_relative_argv(probe):
    stopped, *_ = probe()
    assert stopped["converted"] == stopped["raw"]
    assert stopped["raw"][2:] == SPARSE_ARGS
    assert all(not pattern.startswith("/") for pattern in SPARSE_ARGS[3:])


def test_sparse_tokens_survive_simulated_conversion(probe):
    stopped, env, git, log, worktree = probe(simulate=True)
    assert stopped["converted"][2:] == SPARSE_ARGS
    # Positive control: run the SAME executable with slash-prefixed counterparts.
    # The hand-constructed leading slash must trigger this simulation's corruption.
    slash_args = [*SPARSE_ARGS[:3], *("/" + p for p in SPARSE_ARGS[3:])]
    result = subprocess.run(
        [str(git), "-C", worktree, *slash_args], env=env,
        capture_output=True, text=True, timeout=TIMEOUT,
    )
    assert result.returncode == 1
    control = json.loads(log.read_text().splitlines()[-1])
    assert control["kind"] == "stop"
    assert control["raw"] == ["-C", worktree, *slash_args]
    assert control["converted"][2:] == [
        "sparse-checkout", "set", "--no-cone",
        "converted:/.claude/state/", "converted:/docs/reports/",
        "converted:/scripts/readiness/",
    ]
    assert control["converted"][2:] != slash_args

    # Verify the fail-closed boundary itself, using only the synthetic executable.
    # Neither remote configuration nor publication/mutation is allowlisted.
    guard_log = log.with_name("forbidden.jsonl")
    for command in (
        ["remote", "add", "other", "unused"],
        ["fetch", "other", "main"], ["push", "origin", "HEAD:main"],
        ["commit", "-m", "unused"], ["add", "--all"],
        ["checkout", "--detach", "origin/main"],
    ):
        rejected = subprocess.run(
            [str(git), "-C", env["FIXTURE_REPO"], *command],
            env={**env, "ARGV_LOG": str(guard_log)},
            capture_output=True, text=True, timeout=TIMEOUT,
        )
        assert rejected.returncode == 1
        record = json.loads(guard_log.read_text().splitlines()[-1])
        assert record["kind"] == "forbidden"
        assert record["raw"][2:] == command
