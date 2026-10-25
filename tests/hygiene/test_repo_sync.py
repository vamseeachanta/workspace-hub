"""Sync contract tests with disposable repositories and independent Git history.

Synthetic fixture policy: timeout=10 s, freshness=60 s, bytes=3, age=5 s.
These are test inputs, not operational recommendations. Fast-forward expectations
follow Git merge documentation, --ff-only (Git 2.43.0): the old tip must be an
ancestor of the new tip. Tests construct that graph without the sync code.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("repo_sync", ROOT / "scripts/readiness/repo_hygiene.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def git(repo, *args):
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("GIT_"):
            env.pop(key)
    # Fixture identity only; the repository running the tests is never configured.
    env.update(GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="user.name", GIT_CONFIG_VALUE_0="Test",
               GIT_CONFIG_KEY_1="user.email", GIT_CONFIG_VALUE_1="test")
    return subprocess.check_output(["git", "-C", str(repo), *args], env=env,
                                   stderr=subprocess.DEVNULL, text=True).strip()


@pytest.fixture
def repos(tmp_path):
    remote = tmp_path / "remote.git"
    remote.mkdir()
    git(remote, "init", "--bare", "--initial-branch=main")
    source = tmp_path / "source"
    git(tmp_path, "clone", str(remote), str(source))
    (source / "value").write_text("initial", encoding="utf-8", newline="\n")
    git(source, "add", "value")
    git(source, "commit", "-m", "initial")
    git(source, "push", "origin", "main")
    target = tmp_path / "target"
    git(tmp_path, "clone", str(remote), str(target))
    return source, target, remote


def advance(source):
    (source / "value").write_text("next", encoding="utf-8", newline="\n")
    git(source, "add", "value")
    git(source, "commit", "-m", "next")
    git(source, "push", "origin", "main")
    return git(source, "rev-parse", "HEAD")


def manifest(tmp_path, **changes):
    policy = {"schema_version": 1, "git_timeout_seconds": 10, "max_age_seconds": 60,
              "repos": [{"id": "repo-a", "path": "target", "branch": "main",
                         "activity_lock": "activity.lock"}], "scratch": []}
    policy.update(changes)
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(policy), encoding="utf-8", newline="\n")
    return path


def run(tmp_path, path=None):
    result = subprocess.run(["bash", str(ROOT / "scripts/hygiene/repo-sync.sh"),
                             "--manifest", str(path or manifest(tmp_path)),
                             "--root", str(tmp_path), "--state", str(tmp_path / "status.json")],
                            check=False, capture_output=True, text=True, timeout=30)
    return result, json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))


def test_fast_forward_then_repeat_is_idempotent(tmp_path, repos):
    source, target, _ = repos
    expected = advance(source)
    result, status = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert git(target, "rev-parse", "HEAD") == expected
    assert status["repos"][0]["head"] == expected
    assert status["repos"][0]["status"] == "synced"
    assert run(tmp_path)[0].returncode == 0
    assert git(target, "rev-list", "--count", "HEAD") == "2"


@pytest.mark.parametrize("kind, expected", [("dirty", "dirty"), ("untracked", "dirty"),
    ("ahead", "wedged"), ("diverged", "wedged"), ("branch", "wrong_branch"),
    ("detached", "wrong_branch"), ("busy", "busy"), ("missing", "missing"),
    ("network", "fetch_failed")])
def test_refusal_preserves_checkout(tmp_path, repos, kind, expected):
    source, target, remote = repos
    if kind in {"ahead", "diverged"}:
        (target / "local").write_text("retained", encoding="utf-8", newline="\n")
        git(target, "add", "local")
        git(target, "commit", "-m", "local")
    if kind == "dirty":
        (target / "value").write_text("retained", encoding="utf-8", newline="\n")
    if kind == "untracked":
        (target / "untracked").write_text("retained", encoding="utf-8", newline="\n")
    if kind == "branch":
        git(target, "switch", "-c", "feature")
    if kind == "detached":
        git(target, "switch", "--detach")
    if kind == "busy":
        (tmp_path / "activity.lock").write_text("busy", encoding="utf-8", newline="\n")
    if kind == "missing":
        return_path = manifest(tmp_path, repos=[{"id": "repo-a", "path": "absent",
            "branch": "main", "activity_lock": "activity.lock"}])
    else:
        return_path = manifest(tmp_path)
    if kind == "network":
        git(target, "remote", "set-url", "origin", str(remote / "absent"))
    if kind != "ahead":
        advance(source)
    before = git(target, "rev-parse", "HEAD")
    result, status = run(tmp_path, return_path)
    assert result.returncode != 0
    assert status["repos"][0]["status"] == expected
    assert git(target, "rev-parse", "HEAD") == before
    if kind == "dirty":
        assert (target / "value").read_text(encoding="utf-8") == "retained"
    assert str(tmp_path) not in json.dumps(status)
    assert str(tmp_path) not in result.stderr


def test_success_timestamp_survives_failure_and_recovers(tmp_path, repos):
    assert run(tmp_path)[0].returncode == 0
    old = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))["repos"][0]["last_success_at"]
    (tmp_path / "activity.lock").touch()
    _, failed = run(tmp_path)
    assert failed["repos"][0]["last_success_at"] == old
    # Removal is confined to the disposable fixture; production never deletes data.
    (tmp_path / "activity.lock").unlink()
    assert run(tmp_path)[1]["repos"][0]["status"] == "synced"


def test_other_repositories_continue_after_a_failure(tmp_path, repos):
    path = manifest(tmp_path, repos=[
        {"id": "absent", "path": "absent", "branch": "main", "activity_lock": "absent.lock"},
        {"id": "repo-a", "path": "target", "branch": "main", "activity_lock": "activity.lock"}])
    _, status = run(tmp_path, path)
    assert [r["status"] for r in status["repos"]] == ["missing", "synced"]


@pytest.mark.parametrize("changes", [{"max_age_seconds": 0}, {"git_timeout_seconds": True},
    {"repos": []}, {"scratch": [{"path": "../escape", "max_bytes": 3, "max_age_seconds": 5}]},
    {"repos": [{"id": "repo-a", "path": "../escape", "branch": "main", "activity_lock": "x"}]},
    {"repos": [{"id": "repo-a", "path": "target", "branch": "--invalid", "activity_lock": "x"}]}])
def test_invalid_manifest_fails_before_git(tmp_path, changes):
    path = manifest(tmp_path, **changes)
    with pytest.raises(ValueError):
        sync.load_manifest(path, tmp_path)


def test_symlink_escape_rejected(tmp_path):
    (tmp_path / "escape").symlink_to(tmp_path.parent, target_is_directory=True)
    path = manifest(tmp_path, repos=[{"id": "repo-a", "path": "escape", "branch": "main",
                                     "activity_lock": "activity.lock"}])
    with pytest.raises(ValueError):
        sync.load_manifest(path, tmp_path)


def test_shared_repository_lock_prevents_sync(tmp_path, repos):
    import fcntl
    lock = repos[1] / ".git" / "repo-hygiene.lock"
    with lock.open("w", encoding="utf-8", newline="\n") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert run(tmp_path)[1]["repos"][0]["status"] == "busy"


def test_inherited_git_binding_cannot_redirect_sync(tmp_path, repos, monkeypatch):
    source, target, remote = repos
    expected = advance(source)
    monkeypatch.setenv("GIT_DIR", str(remote))
    monkeypatch.setenv("GIT_WORK_TREE", str(source))
    monkeypatch.setenv("GIT_COMMON_DIR", str(remote))
    assert run(tmp_path)[0].returncode == 0
    assert git(target, "rev-parse", "HEAD") == expected


def test_scratch_inventory_is_report_only(tmp_path, repos):
    """Hand calculation: 4 bytes > input limit 3; age 10 s > input limit 5."""
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    item = scratch / "retained"
    item.write_bytes(b"data")
    os.utime(item, (0, 0))
    path = manifest(tmp_path, scratch=[{"path": "scratch", "max_bytes": 3, "max_age_seconds": 5}])
    _, status = run(tmp_path, path)
    assert status["cleanup"] == {"status": "attention", "bytes": 4, "expired_files": 1}
    assert item.read_bytes() == b"data"


def public_row():
    return {"id": "repo-a", "status": "synced", "dirty": False, "wedged": False,
            "head": "a" * 40, "last_success_at": "2026-01-01T00:00:00+00:00"}


def payload():
    return {"schema_version": 1, "observed_at": "2026-01-01T00:00:00+00:00",
            "max_age_seconds": 60, "repos": [public_row()],
            "cleanup": {"status": "not_evaluated", "bytes": 0, "expired_files": 0}}


def test_public_projection_discards_private_fields():
    data = payload()
    data["private"] = str(Path.cwd())
    data["repos"][0]["remote"] = "private"
    assert sync.public_status(data) == payload()


@pytest.mark.parametrize("tamper", [lambda d: d.update(max_age_seconds=True),
    lambda d: d["repos"][0].update(status="private"),
    lambda d: d["repos"][0].update(dirty="false"),
    lambda d: d["repos"][0].update(head="private"),
    lambda d: d["repos"][0].update(last_success_at="invalid"),
    lambda d: d.update(repos=[]), lambda d: d.update(observed_at="invalid"),
    lambda d: d["cleanup"].update(bytes=-1)])
def test_invalid_public_evidence_is_missing(tamper):
    data = payload()
    tamper(data)
    assert sync.public_status(data) is None


def test_ignored_file_collision_is_preserved(tmp_path, repos):
    """Git merge --no-overwrite-ignore rejects replacing ignored, untracked data."""
    source, target, _ = repos
    (target / ".git" / "info" / "exclude").write_text("retained\n", encoding="utf-8", newline="\n")
    (target / "retained").write_text("local data", encoding="utf-8", newline="\n")
    (source / "retained").write_text("remote data", encoding="utf-8", newline="\n")
    git(source, "add", "retained")
    git(source, "commit", "-m", "track new file")
    git(source, "push", "origin", "main")
    before = git(target, "rev-parse", "HEAD")
    result, _ = run(tmp_path)
    assert result.returncode != 0
    assert (target / "retained").read_text(encoding="utf-8") == "local data"
    assert git(target, "rev-parse", "HEAD") == before


def test_unreadable_scratch_is_an_error(tmp_path, monkeypatch):
    def inaccessible(path, *, followlinks, onerror):
        onerror(PermissionError("unreadable"))
    monkeypatch.setattr(sync.os, "walk", inaccessible)
    (tmp_path / "scratch").mkdir()
    assert sync.scratch_status(tmp_path, [{"path": "scratch", "max_bytes": 3,
        "max_age_seconds": 5}], 10)["status"] == "error"


def test_git_failure_is_reported_without_diagnostics(tmp_path, repos, monkeypatch):
    def failing(*args):
        raise subprocess.TimeoutExpired("private", 10)
    monkeypatch.setattr(sync, "git", failing)
    row = sync.sync_repo(tmp_path, {"id": "repo-a", "path": "target", "branch": "main",
        "activity_lock": "activity.lock"}, 10, {}, "2026-01-01T00:00:00+00:00")
    assert row["status"] == "error"
    assert "private" not in json.dumps(row)


def test_configured_squash_cannot_prevent_fast_forward(tmp_path, repos):
    source, target, _ = repos
    expected = advance(source)
    git(target, "config", "branch.main.mergeOptions", "--squash")
    result, status = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert git(target, "rev-parse", "HEAD") == expected
    assert git(target, "status", "--porcelain=v1") == ""
    assert status["repos"][0]["status"] == "synced"
    assert status["repos"][0]["head"] == expected
    assert status["repos"][0]["dirty"] is False


@pytest.mark.parametrize("condition", ["wrong_head", "dirty"])
def test_merge_postconditions_preserve_prior_success(tmp_path, repos, monkeypatch, condition):
    source, target, _ = repos
    advance(source)
    real_git = sync.git

    def incomplete_merge(repo, timeout, *args):
        if args[0] == "merge":
            if condition == "dirty":
                real_git(repo, timeout, *args)
                (target / "unexpected").write_bytes(b"changed")
            return ""
        return real_git(repo, timeout, *args)

    monkeypatch.setattr(sync, "git", incomplete_merge)
    previous = {"last_success_at": "2026-01-01T00:00:00+00:00"}
    row = sync.sync_repo(tmp_path, {"id": "repo-a", "path": "target", "branch": "main",
        "activity_lock": "activity.lock"}, 10, previous, "2026-01-02T00:00:00+00:00")
    assert row["status"] == ("dirty" if condition == "dirty" else "error")
    assert row["dirty"] is (condition == "dirty")
    assert row["last_success_at"] == previous["last_success_at"]


def test_scratch_inventory_ignores_fifo(tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    regular = scratch / "regular"
    regular.write_bytes(b"data")
    fifo = scratch / "pipe"
    os.mkfifo(fifo)
    os.utime(regular, (10, 10))
    os.utime(fifo, (0, 0))
    # Four regular bytes equal the limit; age zero is within five seconds.
    assert sync.scratch_status(tmp_path, [{"path": "scratch", "max_bytes": 4,
        "max_age_seconds": 5}], 10) == {"status": "clear", "bytes": 4, "expired_files": 0}


def test_scratch_inventory_does_not_walk_junctions(tmp_path, monkeypatch):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    junction = scratch / "junction"
    junction.mkdir()
    (junction / "excluded").write_bytes(b"excluded")
    (scratch / "regular").write_bytes(b"data")
    monkeypatch.setattr(sync.os.path, "isjunction", lambda path: Path(path) == junction, raising=False)
    assert sync.scratch_status(tmp_path, [{"path": "scratch", "max_bytes": 4,
        "max_age_seconds": 5}], 0) == {"status": "clear", "bytes": 4, "expired_files": 0}
