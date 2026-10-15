"""Disposable repositories exercise worktree and blob-filtered clone creation."""
from pathlib import Path
import re
import subprocess

import pytest

from test_worktree_location_guard import NETWORK_TYPES, filesystem_env

ROOT = Path(__file__).resolve().parents[3]
CHECKOUT = ROOT / "scripts/operations/storage/job_checkout.sh"


def git(repo, *args, input=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=input,
                          capture_output=True, check=True).stdout.decode().strip()


@pytest.fixture
def source(tmp_path, monkeypatch):
    # Fixture Git operations must never inherit bindings to the caller's repository.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        monkeypatch.delenv(key, raising=False)
    repo = tmp_path / "digitalmodel.git"
    subprocess.run(["git", "init", "--bare", str(repo)], check=True, capture_output=True)
    # Sparse files keep fixture construction cheap while representing heavy docs.
    heavy = tmp_path / "heavy"
    with heavy.open("wb") as stream:
        stream.seek(2 * 1024 * 1024 - 1)
        stream.write(b"x")
    author = b"fixture <" + b"fixture" + b"@" + b"example" + b"." + b"invalid>"
    docs = heavy.read_bytes()
    history = (
        b"commit refs/heads/main\nmark :1\ncommitter " + author +
        b" 1700000000 +0000\ndata 7\ninitial\nM 100644 inline docs/history.bin\ndata " +
        str(len(docs)).encode() + b"\n" + docs + b"\n\n" +
        b"commit refs/heads/main\ncommitter " + author +
        b" 1700000001 +0000\ndata 7\ncurrent\nfrom :1\nD docs/history.bin\n" +
        b"M 100644 inline docs/current.bin\ndata " + str(len(docs) + 1).encode() +
        b"\n" + docs + b"y\nM 100644 inline src/code.py\ndata 9\nVALUE=42\n\n" +
        b"M 100644 inline README.md\ndata 8\nfixture\n\n")
    git(repo, "fast-import", "--quiet", input=history)
    git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
    git(repo, "config", "uploadpack.allowFilter", "true")
    git(repo, "config", "uploadpack.allowAnySHA1InWant", "true")
    return repo


def run_checkout(source, dest, *args):
    return subprocess.run(["bash", str(CHECKOUT), "--repo", str(source),
                           "--branch", "job-test", "--base", "main",
                           "--dest", str(dest), *args], capture_output=True, text=True)


@pytest.mark.parametrize("profile", [False, True])
def test_worktree(source, tmp_path, monkeypatch, profile):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "checkout with spaces"
    result = run_checkout(source, dest, *(["--profile", "code"] if profile else []))
    assert result.returncode == 0, result.stderr
    assert (dest / "src/code.py").is_file()
    assert (dest / "docs").exists() is not profile
    assert (dest / "README.md").is_file()
    assert git(dest, "branch", "--show-current") == "job-test"
    assert "refs/heads/job-test" in git(source, "show-ref")
    assert "mode=worktree" in result.stdout and "location=ok" in result.stdout
    assert re.search(r"checkout_kb=\d+", result.stdout)
    assert git(dest, "config", "core.untrackedCache") == "true"
    assert git(dest, "config", "lfs.fetchexclude") == "*"


@pytest.mark.parametrize("base", ["main", "origin/main", "refs/heads/main"])
def test_partial_clone(source, tmp_path, monkeypatch, base):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "clone"
    result = run_checkout(source.as_uri(), dest, "--base", base)
    assert result.returncode == 0, result.stderr
    assert "mode=partial-clone" in result.stdout
    assert (dest / "src/code.py").is_file() and (dest / "docs/current.bin").is_file()
    assert git(dest, "config", "remote.origin.promisor") == "true"
    assert git(dest, "config", "remote.origin.partialclonefilter") == "blob:none"
    assert git(dest, "config", "lfs.fetchexclude") == "*"
    missing = git(dest, "rev-list", "--objects", "--all", "--missing=print")
    assert any(line.startswith("?") for line in missing.splitlines())


def test_partial_clone_profile(source, tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "clone"
    result = run_checkout(source.as_uri(), dest, "--profile", "code")
    assert result.returncode == 0, result.stderr
    assert (dest / "src/code.py").exists()
    assert not (dest / "docs").exists()


@pytest.mark.parametrize("remote", [False, True])
def test_dry_run(source, tmp_path, monkeypatch, remote):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "absent" / "checkout"
    before = git(source, "worktree", "list", "--porcelain")
    result = run_checkout(source.as_uri() if remote else source, dest, "--dry-run", "--profile", "code")
    assert result.returncode == 0, result.stderr
    assert "location=ok" in result.stdout
    assert not dest.parent.exists()
    assert git(source, "branch", "--list", "job-test") == ""
    assert git(source, "worktree", "list", "--porcelain") == before


@pytest.mark.parametrize("remote", [False, True])
@pytest.mark.parametrize("dry", [False, True])
@pytest.mark.parametrize("refusal", [3, 4])
def test_refusal_before_git_changes(source, tmp_path, monkeypatch, remote, dry, refusal):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FS_TYPE", "fuseblk" if refusal == 3 else "xfs")
    monkeypatch.setenv("FREE_KB", str(20 * 1024 * 1024))
    dest = tmp_path / "absent" / "checkout"
    before = git(source, "worktree", "list", "--porcelain")
    result = run_checkout(source.as_uri() if remote else source, dest,
                          *(["--dry-run"] if dry else []))
    assert result.returncode == refusal, result.stderr
    assert not dest.parent.exists()
    assert git(source, "branch", "--list", "job-test") == ""
    assert git(source, "worktree", "list", "--porcelain") == before


@pytest.mark.parametrize("args", [[], ["--repo"], ["--unknown"],
                                    ["--repo", "x", "--branch", "x", "--base", "main"]])
def test_usage(args):
    result = subprocess.run(["bash", str(CHECKOUT), *args], capture_output=True, text=True)
    assert result.returncode == 2


@pytest.mark.parametrize("args", [["--profile", "../bad"], ["--profile", "missing"],
                                    ["--branch", "bad branch"], ["--base", "--bad"]])
def test_invalid_options_do_not_create(source, tmp_path, monkeypatch, args):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "checkout"
    result = run_checkout(source, dest, *args)
    assert result.returncode == 2, result.stderr
    assert not dest.exists()
    assert not git(source, "branch", "--list", "job-test")


def test_no_forbidden_git_operations():
    code = CHECKOUT.read_text()
    assert not re.search(r"\bgit\s+lfs\b|--force\b|\bpush\b", code)


def test_lfs_smudge_disabled():
    assert "export GIT_LFS_SKIP_SMUDGE=1" in CHECKOUT.read_text()


def test_profile_clone_does_not_fetch_excluded_blobs(source, tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "clone"
    excluded_oid = git(source, "rev-parse", "main:docs/current.bin")
    result = run_checkout(source.as_uri(), dest, "--profile", "code")
    assert result.returncode == 0, result.stderr
    missing = git(dest, "rev-list", "--objects", "--all", "--missing=print").splitlines()
    assert "?" + excluded_oid in missing


def test_worktree_settings_are_scoped(source, tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    dest = tmp_path / "checkout"
    result = run_checkout(source, dest, "--profile", "code")
    assert result.returncode == 0, result.stderr
    assert git(source, "config", "core.bare") == "true"
    for setting in ("core.untrackedCache", "lfs.fetchexclude", "core.sparseCheckout"):
        absent = subprocess.run(["git", "-C", str(source), "config", "--get", setting],
                                capture_output=True, text=True)
        assert absent.returncode == 1


def test_source_sparse_setting_does_not_make_default_sparse(source, tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    first = tmp_path / "first"
    assert run_checkout(source, first, "--profile", "code").returncode == 0
    dest = tmp_path / "second"
    result = run_checkout(first, dest, "--branch", "second-test")
    assert result.returncode == 0, result.stderr
    assert (dest / "docs/current.bin").is_file()
    assert not (first / "docs").exists()


def test_relative_destination_uses_caller_directory(source, tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("EXPECTED_ANCESTOR", str(tmp_path.resolve()))
    monkeypatch.setenv("FINDMNT_FAIL", "1")
    result = subprocess.run(["bash", str(CHECKOUT), "--repo", str(source),
                             "--branch", "relative-test", "--base", "main",
                             "--dest", "relative checkout"], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    dest = tmp_path / "relative checkout"
    assert (dest / "src/code.py").exists()
    assert not (source / "relative checkout").exists()
    assert str(dest) in git(source, "worktree", "list", "--porcelain")


def test_nonbare_source_configuration_preserved(source, tmp_path, monkeypatch):
    filesystem_env(tmp_path, monkeypatch)
    canonical = tmp_path / "canonical" / "digitalmodel"
    subprocess.run(["git", "clone", "--shared", str(source), str(canonical)],
                   check=True, capture_output=True)
    git(canonical, "config", "core.worktree", str(canonical))
    dest = tmp_path / "checkout"
    result = run_checkout(canonical, dest, "--profile", "code")
    assert result.returncode == 0, result.stderr
    assert git(canonical, "rev-parse", "--show-toplevel") == str(canonical)
    assert git(canonical, "config", "core.bare") == "false"
    assert git(canonical, "config", "core.worktree") == str(canonical)
    assert (canonical / "docs/current.bin").exists()
    assert (dest / "src/code.py").exists() and not (dest / "docs").exists()
    assert git(dest, "rev-parse", "--show-toplevel") == str(dest)


@pytest.mark.parametrize("kind", NETWORK_TYPES)
@pytest.mark.parametrize("remote", [False, True])
@pytest.mark.parametrize("dry", [False, True])
def test_network_refusal_before_git_changes(source, tmp_path, monkeypatch, kind, remote, dry):
    filesystem_env(tmp_path, monkeypatch)
    monkeypatch.setenv("FS_TYPE", kind)
    dest = tmp_path / "absent" / "checkout"
    before = git(source, "worktree", "list", "--porcelain")
    result = run_checkout(source.as_uri() if remote else source, dest,
                          *(["--dry-run"] if dry else []))
    assert result.returncode == 3, result.stdout + result.stderr
    assert kind in result.stderr
    assert not dest.parent.exists()
    assert git(source, "branch", "--list", "job-test") == ""
    assert git(source, "worktree", "list", "--porcelain") == before
