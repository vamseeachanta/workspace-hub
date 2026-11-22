"""State preservation regressions for the daily snapshot commit boundary.

Basis: issue #4027, acceptance and single-file layout amendment (2026).
Expected states are hand-derived: a refused write adds no commit, changes no
index entry, and preserves the previous bytes or the previous absence of a file.
No engineering coefficients or numerical acceptance limits are used.
"""

from __future__ import annotations

import fcntl
import json
import os
import subprocess
import time
from pathlib import Path

import pytest
from test_fleet_snapshot_daily import _make_repo, _run, _test_env

SNAPSHOT = "docs/reports/fleet-snapshots/latest.json"


def _source(tmp_path: Path, map_path: Path) -> Path:
    """Hand mapping: sample-node becomes mac-1; collector stays a public label."""
    map_path.write_text("sample-node mac-1\nfleet-collector fleet-collector\n")
    source = tmp_path / "source.json"
    source.write_text(json.dumps({
        "generated_by": "fleet-collector",
        "machines": [{"name": "sample-node", "reachable": True}],
    }))
    return source


def _env(repo: Path, map_path: Path, source: Path) -> dict[str, str]:
    return _test_env({
        "FLEET_HUB": str(repo),
        "FLEET_LABEL_MAP": str(map_path),
        "FLEET_SNAPSHOT_SOURCE": str(source),
        "FLEET_NO_PUSH": "1",
    })


def _write(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    return _run(["bash", "scripts/fleet/fleet-snapshot-daily.sh"], repo, env=env)


def _without_latest(repo: Path) -> None:
    """Retain the fixture's seed data under another tracked path."""
    _run(["git", "mv", SNAPSHOT, "seed.json"], repo, check=True)
    _run(["git", "commit", "-m", "retain seed outside snapshot directory"],
         repo, check=True)


def test_writer_rechecks_local_edits_after_waiting_for_publish_lock(tmp_path):
    """A write while waiting for the lock must survive, with no new commit."""
    repo, map_path = _make_repo(tmp_path)
    source = _source(tmp_path, map_path)
    head = _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout
    lock_path = repo / ".git" / "fleet-publish.lock"
    with lock_path.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        process = subprocess.Popen(
            ["bash", "scripts/fleet/fleet-snapshot-daily.sh"], cwd=repo,
            env=_env(repo, map_path, source), text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            # Test synchronization budget only; not a production acceptance limit.
            deadline = time.monotonic() + 5
            descriptor = Path("/proc") / str(process.pid) / "fd" / "9"
            while not descriptor.exists() and time.monotonic() < deadline:
                assert process.poll() is None
                time.sleep(0.01)
            assert descriptor.exists(), "writer did not reach the publish lock"
            (repo / SNAPSHOT).write_text("local edit while waiting\n")
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
            stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 2, stdout + stderr
    assert (repo / SNAPSHOT).read_text() == "local edit while waiting\n"
    assert _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout == head
    assert _run(["git", "diff", "--cached", "--name-only"], repo).stdout == ""


def test_failed_first_commit_restores_absent_latest(tmp_path):
    """Absent before + failed commit = absent after, with unchanged HEAD/index."""
    repo, map_path = _make_repo(tmp_path)
    _without_latest(repo)
    source = _source(tmp_path, map_path)
    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/usr/bin/env bash\nexit 1\n")
    hook.chmod(0o755)
    head = _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout
    result = _write(repo, _env(repo, map_path, source))
    assert result.returncode != 0
    assert not (repo / SNAPSHOT).exists()
    assert _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout == head
    assert _run(["git", "status", "--porcelain"], repo).stdout == ""


def test_untracked_latest_is_preserved(tmp_path):
    """An untracked local snapshot is user data, not an empty output slot."""
    repo, map_path = _make_repo(tmp_path)
    _without_latest(repo)
    source = _source(tmp_path, map_path)
    (repo / SNAPSHOT).write_text("untracked local bytes\n")
    head = _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout
    result = _write(repo, _env(repo, map_path, source))
    assert result.returncode == 2
    assert (repo / SNAPSHOT).read_text() == "untracked local bytes\n"
    assert _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout == head


@pytest.mark.parametrize("first_run", [False, True])
def test_latest_only_and_repeated_identical_input_is_noop(tmp_path, first_run):
    """One successful update adds one commit; a repeated input adds none."""
    repo, map_path = _make_repo(tmp_path)
    if first_run:
        _without_latest(repo)
    source = _source(tmp_path, map_path)
    env = _env(repo, map_path, source)
    result = _write(repo, env)
    assert result.returncode == 0, result.stderr
    assert json.loads((repo / SNAPSHOT).read_text()) == {
        "generated_by": "fleet-collector",
        "machines": [{"name": "mac-1", "reachable": True}],
    }
    head = _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout
    assert _write(repo, env).returncode == 0
    assert _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout == head
    assert sorted(p.name for p in (repo / SNAPSHOT).parent.iterdir()) == ["latest.json"]
    assert _run(["git", "status", "--porcelain"], repo).stdout == ""


@pytest.mark.parametrize("failure", ["unknown-name", "missing-map", "invalid-json"])
def test_rejected_input_preserves_head_index_and_latest(tmp_path, failure):
    """Issue #4027: rejected input never reaches the staging boundary."""
    repo, map_path = _make_repo(tmp_path)
    source = _source(tmp_path, map_path)
    env = _env(repo, map_path, source)
    if failure == "unknown-name":
        source.write_text(json.dumps({"machines": [{"name": "unmapped-sample"}]}))
    elif failure == "missing-map":
        env["FLEET_LABEL_MAP"] = str(tmp_path / "missing-map")
    else:
        source.write_text("invalid JSON\n")
    before = (repo / SNAPSHOT).read_bytes()
    head = _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout
    result = _write(repo, env)
    assert result.returncode != 0
    if failure != "invalid-json":
        # Exit contract: fleet_snapshot_labels.py, module docstring (2026).
        assert result.returncode == 2
    assert (repo / SNAPSHOT).read_bytes() == before
    assert _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout == head
    assert _run(["git", "status", "--porcelain"], repo).stdout == ""
    assert "unmapped-sample" not in result.stdout + result.stderr


def test_fixture_environment_keeps_scratch_and_clears_git_bindings(monkeypatch):
    """Child repositories must not resolve the caller's index or working tree."""
    monkeypatch.setenv("GIT_DIR", "caller-metadata")
    monkeypatch.setenv("GIT_WORK_TREE", "caller-tree")
    monkeypatch.setenv("GIT_COMMON_DIR", "caller-common")
    monkeypatch.setenv("GIT_INDEX_FILE", "caller-index")
    monkeypatch.setenv("FLEET_SNAPSHOT_SOURCE", "caller-source")
    env = _test_env({})
    assert not any(key in env for key in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
        "FLEET_SNAPSHOT_SOURCE",
    ))
    assert env.get("TMPDIR") == os.environ.get("TMPDIR")
    assert env.get("PYTHONDONTWRITEBYTECODE") == os.environ.get("PYTHONDONTWRITEBYTECODE")
