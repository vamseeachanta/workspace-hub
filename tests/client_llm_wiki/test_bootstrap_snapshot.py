"""Replacement-free committed template snapshot tests."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from client_llm_wiki import bootstrap_snapshot
from client_llm_wiki.bootstrap_snapshot import (
    BootstrapSnapshotError,
    load_committed_snapshot,
)


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], input=input_bytes, check=True,
        capture_output=True,
    ).stdout


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    _git(tmp_path, "init", str(repo))
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.invalid")
    template = repo / "templates" / "client-llm-wiki"
    template.mkdir(parents=True)
    (template / "plain.txt").write_bytes(b"committed\n")
    executable = template / "tool.sh"
    executable.write_bytes(b"#!/bin/sh\n")
    executable.chmod(0o755)
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "template")
    return repo


def test_snapshot_pins_commit_tree_and_exact_blob_bytes(tmp_path):
    repo = _repo(tmp_path)
    commit = _git(repo, "rev-parse", "HEAD").decode().strip()
    tree = _git(repo, "rev-parse", f"{commit}:templates/client-llm-wiki").decode().strip()
    (repo / "templates/client-llm-wiki/plain.txt").write_bytes(b"dirty\n")

    snapshot = load_committed_snapshot(repo)

    assert snapshot.commit_oid == commit
    assert snapshot.tree_oid == tree
    members = {member.path: member for member in snapshot.members}
    assert members["plain.txt"].data == b"committed\n"
    assert members["plain.txt"].mode == 0o644
    expected_blob = _git(
        repo, "rev-parse", f"{commit}:templates/client-llm-wiki/plain.txt",
    ).decode().strip()
    assert members["plain.txt"].object_oid == expected_blob
    assert members["tool.sh"].mode == 0o755


def test_snapshot_ignores_active_replace_ref(tmp_path):
    repo = _repo(tmp_path)
    original = _git(repo, "rev-parse", "HEAD").decode().strip()
    (repo / "templates/client-llm-wiki/plain.txt").write_bytes(b"replacement\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "replacement")
    replacement = _git(repo, "rev-parse", "HEAD").decode().strip()
    _git(repo, "replace", original, replacement)
    _git(repo, "reset", "--hard", original)

    snapshot = load_committed_snapshot(repo)

    plain = next(member for member in snapshot.members if member.path == "plain.txt")
    assert snapshot.commit_oid == original
    assert plain.data == b"committed\n"


@pytest.mark.parametrize("entry_kind", ["symlink", "gitlink"])
def test_snapshot_rejects_links_and_gitlinks(tmp_path, entry_kind):
    repo = _repo(tmp_path)
    if entry_kind == "symlink":
        (repo / "templates/client-llm-wiki/link").symlink_to("plain.txt")
        _git(repo, "add", ".")
    else:
        oid = _git(repo, "rev-parse", "HEAD").decode().strip()
        _git(
            repo, "update-index", "--add", "--cacheinfo", "160000", oid,
            "templates/client-llm-wiki/nested-repo",
        )
    _git(repo, "commit", "-m", entry_kind)

    with pytest.raises(BootstrapSnapshotError, match="unsupported Git entry"):
        load_committed_snapshot(repo)


@pytest.mark.parametrize(
    "record",
    [
        b"100600 blob " + b"a" * 40 + b"\todd\0",
        b"100644 blob " + b"a" * 40 + b"\t../escape\0",
        b"100644 blob " + b"a" * 40 + b"\t.git\0",
    ],
)
def test_tree_parser_rejects_invalid_modes_and_paths(monkeypatch, record):
    monkeypatch.setattr(bootstrap_snapshot, "_run_git", lambda *_args: record)

    with pytest.raises(BootstrapSnapshotError):
        bootstrap_snapshot._walk_tree(3, "a" * 40)


def test_tree_parser_rejects_duplicate_names(monkeypatch):
    entry = b"100644 blob " + b"a" * 40 + b"\tsame\0"
    monkeypatch.setattr(bootstrap_snapshot, "_run_git", lambda *_args: entry + entry)

    with pytest.raises(BootstrapSnapshotError, match="duplicate"):
        bootstrap_snapshot._tree_entries(3, "a" * 40)


def test_git_calls_have_timeout_and_reject_excess_output(monkeypatch, tmp_path):
    repo = _repo(tmp_path)

    def oversized(_command, **kwargs):
        assert kwargs["timeout"] == 5
        kwargs["stdout"].write(b"x" * 129)
        kwargs["stdout"].flush()
        return subprocess.CompletedProcess([], 0)

    monkeypatch.setattr(bootstrap_snapshot.subprocess, "run", oversized)
    with pytest.raises(BootstrapSnapshotError, match="size limit"):
        load_committed_snapshot(repo)
