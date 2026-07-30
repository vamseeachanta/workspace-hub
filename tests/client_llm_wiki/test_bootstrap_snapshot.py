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
        bootstrap_snapshot._walk_tree(
            bootstrap_snapshot._BoundTemplate(3, 4), "a" * 40,
            bootstrap_snapshot._Budget(),
        )


def test_tree_parser_rejects_duplicate_names(monkeypatch):
    entry = b"100644 blob " + b"a" * 40 + b"\tsame\0"
    monkeypatch.setattr(bootstrap_snapshot, "_run_git", lambda *_args: entry + entry)

    with pytest.raises(BootstrapSnapshotError, match="duplicate"):
        bootstrap_snapshot._tree_entries(
            bootstrap_snapshot._BoundTemplate(3, 4), "a" * 40,
            bootstrap_snapshot._Budget(),
        )


@pytest.mark.parametrize(
    "record",
    [
        b"100644 blob " + b"a" * 40 + b"\tname",
        b"100644 blob " + b"a" * 40 + b"\tname\0\0",
        b"100644 blob " + b"a" * 40 + b"\tbad\nname\0",
        b"100644 blob " + b"a" * 40 + b"\tbad\rname\0",
        b"100644 blob " + b"a" * 40 + b"\tbad\tname\0",
        b"100644 blob " + b"a" * 40 + b"\tbad\x01name\0",
        b"100644 blob " + b"a" * 40 + b"\tbad\x7fname\0",
    ],
)
def test_tree_parser_rejects_malformed_framing_and_controls(monkeypatch, record):
    monkeypatch.setattr(bootstrap_snapshot, "_run_git", lambda *_args: record)
    with pytest.raises(BootstrapSnapshotError):
        bootstrap_snapshot._tree_entries(
            bootstrap_snapshot._BoundTemplate(3, 4), "a" * 40,
            bootstrap_snapshot._Budget(),
        )


def test_git_calls_have_timeout_and_reject_excess_output(monkeypatch, tmp_path):
    repo = _repo(tmp_path)

    def oversized(_command, **kwargs):
        assert kwargs["timeout"] == 5
        kwargs["stdout"].write(b"x" * 4097)
        kwargs["stdout"].flush()
        return subprocess.CompletedProcess([], 0)

    monkeypatch.setattr(bootstrap_snapshot.subprocess, "run", oversized)
    with pytest.raises(BootstrapSnapshotError, match="size limit"):
        load_committed_snapshot(repo)


def test_repeated_blob_oid_is_read_once(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    template = repo / "templates/client-llm-wiki"
    (template / "copy.txt").write_bytes(b"committed\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "duplicate blob")
    calls: list[tuple[str, ...]] = []
    original = bootstrap_snapshot._run_git

    def record(bound, args, limit, budget):
        calls.append(args)
        return original(bound, args, limit, budget)

    monkeypatch.setattr(bootstrap_snapshot, "_run_git", record)
    snapshot = load_committed_snapshot(repo)
    members = {member.path: member for member in snapshot.members}

    assert members["plain.txt"].data is members["copy.txt"].data
    assert sum(args[:2] == ("cat-file", "blob") for args in calls) == 2


def test_wide_and_deep_tree_cumulative_limits_fail_closed(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    deep = repo / "templates/client-llm-wiki/a/b/c"
    deep.mkdir(parents=True)
    (deep / "leaf").write_text("x", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "deep")

    for constant, value, match in (
        ("_MEMBER_LIMIT", 1, "member/path"),
        ("_DEPTH_LIMIT", 1, "depth"),
        ("_PATH_BYTES_LIMIT", 1, "member/path"),
        ("_COMMAND_LIMIT", 1, "command"),
        ("_AGGREGATE_TREE_LIMIT", 1, "tree-output"),
    ):
        with monkeypatch.context() as scoped:
            scoped.setattr(bootstrap_snapshot, constant, value)
            with pytest.raises(BootstrapSnapshotError, match=match):
                load_committed_snapshot(repo)


def test_total_blob_limit_is_checked_before_blob_read(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    calls: list[tuple[str, ...]] = []
    original = bootstrap_snapshot._run_git

    def record(bound, args, limit, budget):
        calls.append(args)
        return original(bound, args, limit, budget)

    monkeypatch.setattr(bootstrap_snapshot, "_TOTAL_BLOB_LIMIT", 1)
    monkeypatch.setattr(bootstrap_snapshot, "_run_git", record)
    with pytest.raises(BootstrapSnapshotError, match="total size"):
        load_committed_snapshot(repo)
    assert not any(args[:2] == ("cat-file", "blob") for args in calls)


def test_linked_worktree_uses_bound_explicit_git_and_worktree_fds(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    linked = tmp_path / "linked"
    _git(repo, "worktree", "add", "-b", "linked-test", str(linked))
    calls: list[tuple[tuple[str, ...], tuple[int, ...]]] = []
    original = subprocess.run

    def record(command, *args, **kwargs):
        calls.append((tuple(str(part) for part in command), kwargs["pass_fds"]))
        return original(command, *args, **kwargs)

    monkeypatch.setattr(bootstrap_snapshot.subprocess, "run", record)
    snapshot = load_committed_snapshot(linked)

    assert snapshot.members
    object_calls = [call for call in calls if "ls-tree" in call[0]]
    object_commands = [call[0] for call in object_calls]
    assert object_commands
    assert all(any(part.startswith("--git-dir=/proc/self/fd/") for part in command) for command in object_commands)
    assert all(any(part.startswith("--work-tree=/proc/self/fd/") for part in command) for command in object_commands)
    assert all("-C" not in command for command in object_commands)
    assert all(len(pass_fds) == 2 for _, pass_fds in object_calls)


def test_post_bind_worktree_path_swap_cannot_redirect_object_reads(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    moved = tmp_path / "held-repo"
    decoy = tmp_path / "repo"
    original = bootstrap_snapshot._run_git
    swapped = False

    def swap(bound, args, limit, budget):
        nonlocal swapped
        if not swapped:
            repo.rename(moved)
            decoy.mkdir()
            swapped = True
        return original(bound, args, limit, budget)

    monkeypatch.setattr(bootstrap_snapshot, "_run_git", swap)
    snapshot = load_committed_snapshot(repo)

    plain = next(member for member in snapshot.members if member.path == "plain.txt")
    assert plain.data == b"committed\n"


def test_post_bind_gitdir_swap_cannot_redirect_object_reads(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    held_git = tmp_path / "held-git"
    original = bootstrap_snapshot._run_git
    swapped = False

    def swap(bound, args, limit, budget):
        nonlocal swapped
        if not swapped:
            (repo / ".git").rename(held_git)
            (repo / ".git").mkdir()
            swapped = True
        return original(bound, args, limit, budget)

    monkeypatch.setattr(bootstrap_snapshot, "_run_git", swap)
    snapshot = load_committed_snapshot(repo)

    plain = next(member for member in snapshot.members if member.path == "plain.txt")
    assert plain.data == b"committed\n"
