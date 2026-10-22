"""Independent Git fixtures for the repository sync helper.

Expected counts follow explicit graph construction: a seed commit shared by both
clones gives (ahead=0, behind=0); one local child gives (1, 0); a remote
child gives (0, 1); distinct children give (1, 1). No production function
computes these expected values. Git semantics: git-rev-list, --left-right
and --count; git-pull, --ff-only; git-push, refspec documentation.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/operations/ws.py"
SPEC = importlib.util.spec_from_file_location("ws", SCRIPT)
ws = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ws)


@pytest.fixture
def git_env(monkeypatch):
    # Ignore caller repository bindings and user configuration in disposable repos.
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")


def git(root, *args, input=None):
    return subprocess.run(
        ["git", "-C", str(root), *args], input=input, text=True,
        capture_output=True, check=True,
    ).stdout.strip()


def child(root, message="child"):
    # fast-import supplies synthetic fixture metadata, without changing identity.
    identity = "Fixture <fixture" + chr(64) + "example.invalid>"
    parent = git(root, "rev-parse", "HEAD")
    branch = git(root, "symbolic-ref", "HEAD")
    stream = (
        f"commit {branch}\ncommitter {identity} 1 +0000\n"
        f"data {len(message)}\n{message}\nfrom {parent}\n\ndone\n"
    )
    git(root, "fast-import", "--quiet", input=stream)


@pytest.fixture
def repos(tmp_path, git_env):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", "--initial-branch=main", str(remote))
    identity = "Fixture <fixture" + chr(64) + "example.invalid>"
    git(remote, "fast-import", "--quiet", input=(
        "commit refs/heads/main\n"
        f"committer {identity} 1 +0000\ndata 4\nseed\n\ndone\n"
    ))
    left, right = tmp_path / "left", tmp_path / "right"
    for root in (left, right):
        git(tmp_path, "clone", str(remote), str(root))
        git(root, "switch", "-c", "feature/sample")
    git(left, "push", "-u", "origin", "feature/sample")
    git(right, "fetch", "origin")
    git(right, "branch", "--set-upstream-to=origin/feature/sample")
    return left, right, remote


def cli(root, command):
    return subprocess.run(
        [sys.executable, str(SCRIPT), command, "--repo", str(root)],
        text=True, capture_output=True, check=False,
    )


def test_equal_and_ahead_counts(repos):
    left, _, _ = repos
    state = ws.status(left)
    assert (state["ahead"], state["behind"], state["dirty"]) == (0, 0, False)
    child(left)
    state = ws.status(left)
    assert (state["ahead"], state["behind"]) == (1, 0)
    assert state["comparison"] == "local-tracking-ref"


def test_status_does_not_fetch(repos):
    left, right, _ = repos
    child(right)
    git(right, "push")
    assert ws.status(left)["behind"] == 0
    git(left, "fetch", "origin")
    assert ws.status(left)["behind"] == 1


def test_pull_fast_forwards(repos):
    left, right, _ = repos
    child(right)
    git(right, "push")
    ws.sync(left, "pull")
    assert git(left, "rev-parse", "HEAD") == git(right, "rev-parse", "HEAD")


def test_pull_divergence_preserves_local_head(repos):
    left, right, _ = repos
    child(left, "local")
    child(right, "remote")
    git(right, "push")
    before = git(left, "rev-parse", "HEAD")
    with pytest.raises(ws.SyncError):
        ws.sync(left, "pull")
    assert git(left, "rev-parse", "HEAD") == before
    assert (ws.status(left)["ahead"], ws.status(left)["behind"]) == (1, 1)


def test_push_publishes_only_selected_branch(repos):
    left, _, remote = repos
    main = git(remote, "rev-parse", "main")
    child(left)
    ws.sync(left, "push")
    assert git(remote, "rev-parse", "feature/sample") == git(left, "rev-parse", "HEAD")
    assert git(remote, "rev-parse", "main") == main


@pytest.mark.parametrize("command", ["pull", "push"])
def test_dirty_tree_refused(repos, command):
    left, _, _ = repos
    (left / "untracked.txt").write_text("preserve me", encoding="utf-8")
    before = git(left, "rev-parse", "HEAD")
    with pytest.raises(ws.SyncError, match="uncommitted"):
        ws.sync(left, command)
    assert git(left, "rev-parse", "HEAD") == before
    assert (left / "untracked.txt").read_text() == "preserve me"


def test_protected_source_branch_refused(repos):
    left, _, _ = repos
    git(left, "switch", "main")
    with pytest.raises(ws.SyncError, match="protected"):
        ws.sync(left, "push")


def test_protected_destination_refused(repos):
    left, _, _ = repos
    git(left, "branch", "--set-upstream-to=origin/main")
    with pytest.raises(ws.SyncError, match="protected"):
        ws.sync(left, "push")


@pytest.mark.parametrize("command", ["pull", "push"])
def test_missing_upstream_refused(repos, command):
    left, _, _ = repos
    git(left, "branch", "--unset-upstream")
    assert ws.status(left)["ahead"] is None
    with pytest.raises(ws.SyncError, match="upstream"):
        ws.sync(left, command)


def test_detached_refused(repos):
    left, _, _ = repos
    git(left, "switch", "--detach")
    assert ws.status(left)["branch"] is None
    with pytest.raises(ws.SyncError, match="detached"):
        ws.sync(left, "pull")


def test_worktree_and_nested_directory(repos, tmp_path):
    left, _, _ = repos
    tree = tmp_path / "linked tree"
    git(left, "worktree", "add", "-b", "feature/linked", str(tree))
    nested = tree / "nested"
    nested.mkdir()
    assert (tree / ".git").is_file()
    assert ws.status(nested)["branch"] == "feature/linked"


def test_inherited_git_binding_does_not_redirect(repos, monkeypatch):
    left, right, _ = repos
    (right / "changed").write_text("other repository", encoding="utf-8")
    before = {
        p.relative_to(right): p.read_bytes()
        for p in right.rglob("*") if p.is_file()
    }
    for key in ("GIT_DIR", "GIT_COMMON_DIR"):
        monkeypatch.setenv(key, str(right / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(right))
    monkeypatch.setenv("GIT_INDEX_FILE", str(right / ".git/alternate-index"))
    assert ws.status(left)["dirty"] is False
    after = {
        p.relative_to(right): p.read_bytes()
        for p in right.rglob("*") if p.is_file()
    }
    assert after == before
    assert (right / "changed").read_text() == "other repository"
    assert not (right / ".git/alternate-index").exists()


def test_non_repository_reports_no_paths(tmp_path, git_env):
    result = cli(tmp_path, "status")
    assert result.returncode == 1
    assert str(tmp_path) not in result.stderr
    assert "Traceback" not in result.stderr


def test_unborn_repository(tmp_path, git_env):
    git(tmp_path, "init", "--initial-branch=main")
    state = ws.status(tmp_path)
    assert state["branch"] == "main"
    assert state["ahead"] is None


def test_status_cli_json(repos):
    left, _, _ = repos
    result = cli(left, "status")
    assert result.returncode == 0
    assert json.loads(result.stdout)["branch"] == "feature/sample"


def test_doctor_uses_presence_only(monkeypatch):
    calls = []

    def which(name):
        calls.append(name)
        return "installed" if name != "python3" else None

    monkeypatch.setattr(ws.shutil, "which", which)
    report = ws.doctor()
    assert calls == ["git", "gh", "node", "python3", "claude", "codex"]
    assert report["tools"]["python3"] == "missing"
    assert report["ready"] is False
    assert report["versions"] == "not-evaluated"


def test_git_failure_redacts_remote_details(monkeypatch, tmp_path):
    def failure(*args, **kwargs):
        return subprocess.CompletedProcess(args, 128, "", "sensitive remote detail")

    monkeypatch.setattr(ws.subprocess, "run", failure)
    with pytest.raises(ws.SyncError) as error:
        ws.status(tmp_path)
    assert "sensitive" not in str(error.value)


def test_non_fast_forward_push_preserves_remote(repos):
    left, right, remote = repos
    child(left, "local")
    child(right, "remote")
    git(right, "push")
    before = git(remote, "rev-parse", "feature/sample")
    with pytest.raises(ws.SyncError):
        ws.sync(left, "push")
    assert git(remote, "rev-parse", "feature/sample") == before


@pytest.mark.parametrize("command", ["pull", "push"])
def test_staged_change_refused(repos, command):
    left, _, _ = repos
    (left / "staged").write_text("keep staged", encoding="utf-8")
    git(left, "add", "staged")
    before = (left / ".git/index").read_bytes()
    with pytest.raises(ws.SyncError, match="uncommitted"):
        ws.sync(left, command)
    assert (left / ".git/index").read_bytes() == before


@pytest.mark.parametrize("marker", ["MERGE_HEAD", "rebase-merge", "CHERRY_PICK_HEAD"])
def test_unfinished_operation_refused(repos, marker):
    left, _, _ = repos
    path = left / ".git" / marker
    if marker == "rebase-merge":
        path.mkdir()
    else:
        path.write_text(git(left, "rev-parse", "HEAD") + "\n", encoding="utf-8")
    with pytest.raises(ws.SyncError, match="unfinished"):
        ws.sync(left, "push")


def test_local_upstream_refused(repos):
    left, _, _ = repos
    git(left, "branch", "--set-upstream-to=main")
    with pytest.raises(ws.SyncError, match="local branch"):
        ws.sync(left, "push")


def test_missing_git_is_actionable(monkeypatch, tmp_path):
    def missing(*args, **kwargs):
        raise FileNotFoundError("private executable path")

    monkeypatch.setattr(ws.subprocess, "run", missing)
    with pytest.raises(ws.SyncError, match="could not start") as error:
        ws.status(tmp_path)
    assert "private" not in str(error.value)


def test_bare_repository_refused(repos):
    _, _, remote = repos
    with pytest.raises(ws.SyncError, match="working tree"):
        ws.status(remote)


def test_unknown_operation_refused(repos):
    left, _, _ = repos
    with pytest.raises(ws.SyncError, match="Unknown"):
        ws.sync(left, "rewrite")


def test_doctor_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(ws.shutil, "which", lambda name: None)
    assert ws.main(["doctor"]) == 1
    assert json.loads(capsys.readouterr().out)["ready"] is False


def test_push_does_not_follow_configured_tags(repos):
    left, _, remote = repos
    child(left)
    git(left, "config", "push.followTags", "true")
    # fast-import creates an annotated tag without changing Git user identity.
    identity = "Fixture <fixture" + chr(64) + "example.invalid>"
    git(left, "fast-import", "--quiet", input=(
        f"tag sample\nfrom {git(left, 'rev-parse', 'HEAD')}\n"
        f"tagger {identity} 1 +0000\ndata 3\ntag\ndone\n"
    ))
    ws.sync(left, "push")
    assert git(remote, "tag", "--list") == ""


def test_inventory_compares_explicit_names(repos, tmp_path):
    (tmp_path / "artifacts").mkdir()
    report = ws.inventory(tmp_path, ["left", "right", "absent"])
    assert report["repositories"] == ["left", "right"]
    assert report["missing"] == ["absent"]
    assert report["unexpected"] == []
    assert report["unmanaged"] == ["artifacts", "remote.git"]
    assert report["ready"] is False


def test_inventory_without_expected_set_is_unqualified(repos, tmp_path):
    report = ws.inventory(tmp_path, [])
    assert report["ready"] is None
    assert report["criterion"] == "not-supplied"


def test_inventory_worktree(repos, tmp_path):
    left, _, _ = repos
    git(left, "worktree", "add", "-b", "feature/inventory", str(tmp_path / "linked"))
    report = ws.inventory(tmp_path, ["left", "right", "linked"])
    assert report["repositories"] == ["left", "linked", "right"]
    assert report["ready"] is True


@pytest.mark.parametrize("name", ["../outside", "nested/repo", "nested\\repo", ".", ".."])
def test_inventory_rejects_path_criteria(tmp_path, name):
    with pytest.raises(ws.SyncError, match="folder names"):
        ws.inventory(tmp_path, [name])


def test_inventory_invalid_marker_not_qualified(repos, tmp_path):
    invalid = tmp_path / "invalid"
    invalid.mkdir()
    (invalid / ".git").write_text("invalid", encoding="utf-8")
    report = ws.inventory(tmp_path, ["invalid", "left", "right"])
    assert report["unverified"] == ["invalid"]
    assert report["missing"] == ["invalid"]
    assert report["ready"] is False


def test_inventory_does_not_follow_symlinks(repos, tmp_path):
    try:
        (tmp_path / "alias").symlink_to(repos[0], target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlink creation is unavailable")
    report = ws.inventory(tmp_path, ["left", "right"])
    assert report["excluded_links"] == ["alias"]
    assert "alias" not in report["repositories"]


def test_inventory_invalid_root(tmp_path):
    with pytest.raises(ws.SyncError, match="root"):
        ws.inventory(tmp_path / "absent", [])


def test_inventory_cli(repos, tmp_path, capsys):
    assert ws.main([
        "inventory", "--root", str(tmp_path), "--expect", "left", "right",
    ]) == 0
    assert json.loads(capsys.readouterr().out)["ready"] is True


def test_inventory_cli_requires_root():
    with pytest.raises(SystemExit) as error:
        ws.main(["inventory"])
    assert error.value.code == 2
