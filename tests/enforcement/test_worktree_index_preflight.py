"""Git 2.43 worktree/sparse-checkout contracts, using disposable repositories.

Independent oracle: HEAD contains keep/a.txt and omit/b.txt, hence two leaves.
An initialized index contains those two leaves even if one is skip-worktree.
An interrupted --no-checkout preparation contains zero entries and is refused.
No percentage or performance threshold is used.
"""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/enforcement/check-worktree-index.sh"


@pytest.fixture
def clean_env(monkeypatch):
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                "GIT_CONFIG", "GIT_PREFIX"):
        monkeypatch.delenv(key, raising=False)


def git(repo, *args, input=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=input,
                          capture_output=True, check=True).stdout


@pytest.fixture
def repo(tmp_path, clean_env):
    root = tmp_path / "main"
    root.mkdir()
    git(root, "init", "-q")
    for name in ("keep/a.txt", "omit/b.txt"):
        path = root / name
        path.parent.mkdir(exist_ok=True)
        path.write_text("fixture\n")
    git(root, "add", ".")
    # commit-tree avoids executing any installed hook or changing Git identity.
    tree = git(root, "write-tree").strip().decode()
    env = dict(os.environ)
    address = "fixture" + "@" + "example" + ".invalid"
    for prefix in ("GIT_AUTHOR", "GIT_COMMITTER"):
        env[prefix + "_NAME"] = "Fixture"
        env[prefix + "_EMAIL"] = address
    commit = subprocess.run(["git", "-C", str(root), "commit-tree", tree],
                            input=b"fixture\n", env=env, check=True,
                            capture_output=True).stdout.strip().decode()
    git(root, "update-ref", "HEAD", commit)
    return root


def preflight(repo, *args, env=None):
    return subprocess.run(["bash", str(SCRIPT), str(repo), *args],
                          capture_output=True, text=True, env=env, check=False)


def test_interrupted_no_checkout_is_refused(repo, tmp_path):
    wt = tmp_path / "interrupted"
    git(repo, "worktree", "add", "--detach", "--no-checkout", str(wt))
    result = preflight(wt)
    assert result.returncode == 1
    assert "empty index" in result.stderr
    assert "recreate" in result.stderr


@pytest.mark.parametrize("mode", ["full", "cone", "non-cone", "sparse-index"])
def test_valid_worktrees(repo, tmp_path, mode):
    wt = tmp_path / "linked"
    git(repo, "worktree", "add", "--detach", str(wt))
    if mode != "full":
        if mode == "non-cone":
            git(wt, "sparse-checkout", "set", "--no-cone", "/keep/")
        else:
            git(wt, "sparse-checkout", "set", "--cone", "keep")
            if mode == "sparse-index":
                git(wt, "sparse-checkout", "reapply", "--sparse-index")
        assert b"S " in git(wt, "ls-files", "-t")
    result = preflight(wt, "--fresh")
    assert result.returncode == 0, result.stderr
    assert "head=2 index=2" in result.stdout


def test_full_primary(repo):
    assert preflight(repo).returncode == 0


def test_fresh_whole_tree_deletion_with_added_entry(repo, tmp_path):
    wt = tmp_path / "linked"
    git(repo, "worktree", "add", "--detach", str(wt))
    git(wt, "sparse-checkout", "set", "--cone", "keep")
    git(wt, "read-tree", "--empty")
    (wt / "replacement.txt").write_text("new\n")
    git(wt, "add", "replacement.txt")
    result = preflight(wt, "--fresh")
    assert result.returncode == 1
    assert "whole-tree deletions" in result.stderr


def test_foreign_hook_bindings_are_ignored(repo, tmp_path):
    other = tmp_path / "other"
    git(repo, "worktree", "add", "--detach", "--no-checkout", str(other))
    env = dict(os.environ, GIT_DIR=str(other / ".git"), GIT_WORK_TREE=str(other),
               GIT_INDEX_FILE=str(other / "absent-index"))
    assert preflight(repo, env=env).returncode == 0


def test_corrupt_index_fails_even_in_conditional_call(repo):
    """A Git read failure must not become a zero count when errexit is suppressed."""
    import hashlib

    index = repo / ".git/index"
    original = index.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    index.write_bytes(b"invalid index fixture\n")
    tampered = hashlib.sha256(index.read_bytes()).hexdigest()
    command = 'source "$1"; if worktree_index_preflight "$2"; then exit 0; else exit "$?"; fi'
    result = subprocess.run(["bash", "-c", command, "--",
                             str(ROOT / "scripts/lib/worktree-index.sh"), str(repo)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert hashlib.sha256(index.read_bytes()).hexdigest() == tampered
    index.write_bytes(original)
    assert hashlib.sha256(index.read_bytes()).hexdigest() == before
    assert preflight(repo).returncode == 0


def test_committed_empty_tree_is_valid(repo):
    """Git's empty tree has no leaves; zero index entries are then consistent."""
    tree = git(repo, "mktree", input=b"").decode().strip()
    env = dict(os.environ)
    for prefix in ("GIT_AUTHOR", "GIT_COMMITTER"):
        env[prefix + "_NAME"] = "Fixture"
        env[prefix + "_EMAIL"] = "fixture" + "@" + "example" + ".invalid"
    commit = subprocess.run(["git", "-C", str(repo), "commit-tree", tree],
                            input=b"empty\n", env=env, check=True,
                            capture_output=True).stdout.decode().strip()
    git(repo, "update-ref", "HEAD", commit)
    git(repo, "read-tree", "--empty")
    result = preflight(repo, "--fresh")
    assert result.returncode == 0
    assert "head=0 index=0" in result.stdout
