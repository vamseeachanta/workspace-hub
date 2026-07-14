"""Raw Git audit coverage for rule-authority Phase A2."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_git  # noqa: E402
from rule_authority.structural import SensitiveArtifacts  # noqa: E402


SENSITIVE = SensitiveArtifacts(
    key=b"k" * 32,
    decoded_patterns=(b"synthetic-block-value",),
    exact_artifacts=(),
    prohibited_basenames=frozenset({"sealed.bin"}),
)


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1"}
    result = subprocess.run(
        ["git", *args], cwd=repo, input=input_bytes, capture_output=True, env=env, check=True
    )
    return result.stdout


def _repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Synthetic")
    _git(repo, "config", "user.email", "synthetic@example.invalid")
    (repo / "safe.txt").write_bytes(b"safe\n")
    _git(repo, "add", "--", "safe.txt")
    _git(repo, "commit", "-qm", "initial")
    return repo, _git(repo, "rev-parse", "HEAD").decode().strip()


def test_parse_ls_tree_preserves_arbitrary_path_bytes() -> None:
    raw = b"100644 blob " + b"a" * 40 + b"\tbad-\xff-name\x00"
    entries = audit_git.parse_ls_tree(raw, max_entries=2)
    assert entries == [(b"bad-\xff-name", b"a" * 40, b"blob")]


def test_parse_ls_tree_rejects_malformed_and_cap() -> None:
    with pytest.raises(audit_git.CoverageError):
        audit_git.parse_ls_tree(b"not-a-record\x00", max_entries=2)
    record = b"100644 blob " + b"a" * 40 + b"\ta\x00"
    with pytest.raises(audit_git.CoverageError):
        audit_git.parse_ls_tree(record * 2, max_entries=1)


def test_audit_tree_reads_named_commit_not_worktree(tmp_path: Path) -> None:
    repo, oid = _repo(tmp_path)
    (repo / "safe.txt").write_bytes(b"synthetic-block-value\n")
    result = audit_git.audit_tree(repo, oid, SENSITIVE, max_entries=10, max_blob_bytes=100)
    assert result.verdict == "clean"
    assert result.objects_examined >= 2
    assert result.private_findings == ()


def test_audit_tree_scans_raw_blob_and_path_bytes(tmp_path: Path) -> None:
    repo, _ = _repo(tmp_path)
    raw_name = b"opaque-\xff"
    blob = _git(repo, "hash-object", "-w", "--stdin", input_bytes=b"synthetic-block-value")
    entry = b"100644 blob " + blob.strip() + b"\t" + raw_name + b"\x00"
    tree = _git(repo, "mktree", "-z", input_bytes=entry).strip().decode()
    commit = _git(repo, "commit-tree", tree, "-m", "synthetic").strip().decode()
    result = audit_git.audit_tree(repo, commit, SENSITIVE, max_entries=10, max_blob_bytes=100)
    assert result.verdict == "blocked"
    assert len(result.private_findings) == 1


def test_audit_tree_rejects_symbolic_revision_and_large_blob(tmp_path: Path) -> None:
    repo, oid = _repo(tmp_path)
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_tree(repo, "HEAD", SENSITIVE, max_entries=10, max_blob_bytes=100)
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_tree(repo, oid, SENSITIVE, max_entries=10, max_blob_bytes=2)


def test_audit_index_uses_staged_blob_not_worktree(tmp_path: Path) -> None:
    repo, _ = _repo(tmp_path)
    (repo / "safe.txt").write_bytes(b"synthetic-block-value")
    staged = audit_git.audit_index(repo, SENSITIVE, max_entries=10, max_blob_bytes=100)
    assert staged.verdict == "clean"
    _git(repo, "add", "--", "safe.txt")
    staged = audit_git.audit_index(repo, SENSITIVE, max_entries=10, max_blob_bytes=100)
    assert staged.verdict == "blocked"


def test_ref_snapshot_preserves_ref_bytes_and_rejects_malformed() -> None:
    raw = b"a" * 40 + b"\trefs/heads/main\n" + b"b" * 40 + b"\trefs/pull/1/head\n"
    snapshot = audit_git.parse_ls_remote(raw, max_refs=3)
    assert snapshot.refs[1].name == b"refs/pull/1/head"
    assert len(snapshot.identity) == 64
    with pytest.raises(audit_git.CoverageError):
        audit_git.parse_ls_remote(b"bad\n", max_refs=3)


def test_ref_snapshot_cap_and_drift_fail_closed() -> None:
    first = audit_git.parse_ls_remote(b"a" * 40 + b"\trefs/heads/main\n", max_refs=2)
    second = audit_git.parse_ls_remote(b"b" * 40 + b"\trefs/heads/main\n", max_refs=2)
    with pytest.raises(audit_git.CoverageError):
        audit_git.require_stable_snapshot(first, second)
    with pytest.raises(audit_git.CoverageError):
        audit_git.parse_ls_remote(
            b"a" * 40 + b"\trefs/a\n" + b"b" * 40 + b"\trefs/b\n", max_refs=1
        )


def test_reverse_edges_retain_every_ref_and_path() -> None:
    edges = audit_git.ReachabilityGraph(max_edges=4)
    edges.add(b"ref", b"commit")
    edges.add(b"ref-2", b"commit")
    edges.add(b"commit", b"raw-path")
    assert len(edges.edges) == 3
    with pytest.raises(audit_git.CoverageError):
        for index in range(3):
            edges.add(str(index).encode(), b"overflow")


def test_git_runner_uses_argv_and_sanitized_environment(tmp_path: Path) -> None:
    repo, oid = _repo(tmp_path)
    runner = audit_git.GitRunner(repo)
    assert runner.run("cat-file", "-t", oid).strip() == b"commit"
    with pytest.raises(audit_git.CoverageError):
        runner.run("cat-file", "-t", "$(touch injected)")
    assert not (repo / "injected").exists()


def test_git_runner_retains_repository_dirfd_across_path_swap(tmp_path: Path) -> None:
    repo, oid = _repo(tmp_path)
    runner = audit_git.GitRunner(repo)
    moved = tmp_path / "original"
    repo.rename(moved)
    repo.mkdir()
    try:
        assert runner.run("cat-file", "-t", oid).strip() == b"commit"
    finally:
        runner.close()


def _bare_history(tmp_path: Path) -> tuple[Path, audit_git.RefSnapshot]:
    source, oid = _repo(tmp_path)
    _git(source, "tag", "-a", "v1", "-m", "synthetic-block-value")
    bare = tmp_path / "mirror.git"
    _git(tmp_path, "clone", "-q", "--mirror", str(source), str(bare))
    os.chmod(bare, 0o700)
    head = _git(source, "rev-parse", "HEAD").strip()
    tag = _git(source, "rev-parse", "refs/tags/v1").strip()
    raw = head + b"\trefs/heads/master\n" + tag + b"\trefs/tags/v1\n"
    return bare, audit_git.parse_ls_remote(raw, max_refs=5)


def test_audit_history_scans_tags_and_retains_reverse_edges(tmp_path: Path) -> None:
    bare, snapshot = _bare_history(tmp_path)
    result = audit_git.audit_history(
        bare, snapshot, snapshot, SENSITIVE,
        max_entries=20, max_blob_bytes=100, max_objects=20, max_edges=50,
    )
    assert result.verdict == "blocked"
    assert any(edge[0] == b"refs/tags/v1" for edge in result.edges)
    assert result.objects_examined >= 4


def test_audit_history_requires_bare_complete_stable_mirror(tmp_path: Path) -> None:
    bare, snapshot = _bare_history(tmp_path)
    changed = audit_git.RefSnapshot(snapshot.refs[:-1], "different")
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_history(
            bare, snapshot, changed, SENSITIVE,
            max_entries=20, max_blob_bytes=100, max_objects=20, max_edges=50,
        )
    _git(bare, "config", "remote.origin.promisor", "true")
    with pytest.raises(audit_git.CoverageError):
        audit_git.audit_history(
            bare, snapshot, snapshot, SENSITIVE,
            max_entries=20, max_blob_bytes=100, max_objects=20, max_edges=50,
        )
