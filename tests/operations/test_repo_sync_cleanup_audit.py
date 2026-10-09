"""Fixture-backed tests for the repo-sync cleanup audit port."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "operations" / "repo_sync_cleanup_audit.py"


def load_module():
    spec = importlib.util.spec_from_file_location("repo_sync_cleanup_audit", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["repo_sync_cleanup_audit"] = module
    spec.loader.exec_module(module)
    return module


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=check,
    )


def commit_file(repo: Path, name: str, content: str, message: str) -> None:
    (repo / name).write_text(content)
    run_git(repo, "add", name)
    run_git(
        repo,
        "-c",
        "user.email=test@example.invalid",
        "-c",
        "user.name=Test User",
        "commit",
        "-m",
        message,
    )


def init_repo(path: Path, *, remote_name: str = "origin") -> Path:
    path.mkdir(parents=True)
    run_git(path, "init", "-b", "main")
    commit_file(path, "README.md", f"# {path.name}\n", "initial")
    bare = path.parent / "remotes" / f"{path.name}.git"
    bare.parent.mkdir(exist_ok=True)
    run_git(path, "init", "--bare", str(bare))
    run_git(path, "remote", "add", remote_name, str(bare))
    run_git(path, "push", "-u", remote_name, "main")
    return bare


def init_master_repo(path: Path) -> None:
    path.mkdir(parents=True)
    run_git(path, "init", "-b", "master")
    commit_file(path, "README.md", f"# {path.name}\n", "initial")
    bare = path.parent / "remotes" / f"{path.name}.git"
    bare.parent.mkdir(exist_ok=True)
    run_git(path, "init", "--bare", "--initial-branch=master", str(bare))
    run_git(path, "remote", "add", "origin", str(bare))
    run_git(path, "push", "-u", "origin", "master")


def audit_one(repo: Path, *, public_parent: bool = False) -> dict:
    module = load_module()
    return module.audit_path(repo, public_parent=public_parent)


def finding_codes(row: dict) -> set[str]:
    return {finding["code"] for finding in row["findings"]}


def test_unrelated_history_reports_status_instead_of_unique_count(tmp_path: Path) -> None:
    repo = tmp_path / "unrelated"
    init_repo(repo)
    run_git(repo, "checkout", "--orphan", "topic")
    run_git(repo, "rm", "-rf", ".")
    commit_file(repo, "topic.txt", "topic\n", "orphan topic")

    row = audit_one(repo)

    assert "UNRELATED-HISTORY" in finding_codes(row)
    assert row["unique_commit_count"] is None
    assert not any(f["code"] == "UNPUSHED" for f in row["findings"])


def test_unrelated_history_uses_origin_master_default(tmp_path: Path) -> None:
    repo = tmp_path / "origin-master"
    init_master_repo(repo)
    run_git(repo, "checkout", "--orphan", "main")
    run_git(repo, "rm", "-rf", ".")
    commit_file(repo, "main.txt", "main\n", "orphan main")

    row = audit_one(repo)

    assert row["default_ref"] == "origin/master"
    assert row["unique_commit_count"] is None
    assert "UNRELATED-HISTORY" in finding_codes(row)


def test_same_name_remote_branch_prevents_false_unpushed(tmp_path: Path) -> None:
    repo = tmp_path / "same-name"
    init_repo(repo)
    run_git(repo, "switch", "-c", "feature/o03")
    commit_file(repo, "feature.txt", "feature\n", "feature commit")
    run_git(repo, "push", "-u", "origin", "feature/o03")

    row = audit_one(repo)

    assert row["same_name_remote_branches"] == ["origin/feature/o03"]
    assert "UNPUSHED" not in finding_codes(row)


def test_same_name_branch_on_secondary_remote_is_checked(tmp_path: Path) -> None:
    repo = tmp_path / "secondary-remote"
    init_repo(repo)
    secondary = tmp_path / "remotes" / "secondary.git"
    run_git(repo, "init", "--bare", str(secondary))
    run_git(repo, "remote", "add", "secondary", str(secondary))
    run_git(repo, "switch", "-c", "feature/o03-secondary")
    commit_file(repo, "secondary.txt", "secondary\n", "secondary remote commit")
    run_git(repo, "push", "-u", "secondary", "feature/o03-secondary")

    row = audit_one(repo)

    assert row["same_name_remote_branches"] == ["secondary/feature/o03-secondary"]
    assert "UNPUSHED" not in finding_codes(row)


def test_similar_suffix_remote_branch_does_not_suppress_unpushed(tmp_path: Path) -> None:
    repo = tmp_path / "suffix-main"
    init_repo(repo)
    commit_file(repo, "local.txt", "local main\n", "local main commit")
    run_git(repo, "push", "origin", "HEAD:refs/heads/feature/main")

    row = audit_one(repo)

    assert row["same_name_remote_branches"] == ["origin/main"]
    assert "UNPUSHED" in finding_codes(row)


def test_non_git_directory_is_not_a_sparse_checkout_anomaly(tmp_path: Path) -> None:
    directory = tmp_path / "scratch"
    directory.mkdir()

    row = audit_one(directory)

    assert row["status"] == "NOT-A-REPO"
    assert finding_codes(row) == {"NOT-A-REPO"}


def test_inaccessible_child_does_not_abort_root_audit(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "root"
    root.mkdir()
    blocked = root / "blocked"
    blocked.mkdir()
    module = load_module()

    def deny_on_blocked(repo: Path, *args: str, check: bool = False):
        if repo == blocked.resolve():
            raise PermissionError("denied")
        return run_git(repo, *args, check=check)

    monkeypatch.setattr(module, "run_git", deny_on_blocked)

    rows = module.audit_root(root)

    assert rows[0]["path"] == str(blocked.resolve())
    assert rows[0]["status"] == "NOT-A-REPO"


def test_tracked_missing_files_are_separate_from_modified_files(tmp_path: Path) -> None:
    repo = tmp_path / "missing"
    init_repo(repo)
    commit_file(repo, "tracked.txt", "tracked\n", "tracked file")
    (repo / "tracked.txt").unlink()
    (repo / "README.md").write_text("# modified\n")

    row = audit_one(repo)

    assert row["tracked_missing_count"] == 1
    assert row["modified_count"] == 1
    assert {"TRACKED-MISSING", "MODIFIED"} <= finding_codes(row)


def test_nested_full_clone_inside_public_worktree_is_privacy_risk(tmp_path: Path) -> None:
    parent = tmp_path / "public-parent"
    init_repo(parent)
    nested = parent / "private-client"
    init_repo(nested)

    row = audit_one(parent, public_parent=True)

    assert row["nested_clone_count"] == 1
    assert any(
        finding["code"] == "PRIVACY-NESTED-CLONE"
        and "private repo inside public worktree" in finding["message"]
        for finding in row["findings"]
    )


def test_uv_cache_git_metadata_is_not_a_nested_clone_finding(tmp_path: Path) -> None:
    parent = tmp_path / "public-parent-cache"
    init_repo(parent)
    cached = parent / ".claude" / "state" / "uv-cache" / "sdists-v9"
    cached.mkdir(parents=True)
    (cached / ".git").mkdir()

    row = audit_one(parent, public_parent=True)

    assert row["nested_clone_count"] == 0
    assert "PRIVACY-NESTED-CLONE" not in finding_codes(row)


def test_git_environment_does_not_override_audit_cwd(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "target"
    contaminant = tmp_path / "contaminant"
    init_repo(target)
    init_repo(contaminant)
    commit_file(contaminant, "only-contaminant.txt", "wrong repo\n", "contaminant")
    monkeypatch.setenv("GIT_DIR", str(contaminant / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(contaminant))
    monkeypatch.setenv("GIT_COMMON_DIR", str(contaminant / ".git"))

    row = audit_one(target)

    assert row["path"] == str(target.resolve())
    assert row["status"] == "OK"


def test_nested_gitfile_clone_inside_public_worktree_is_privacy_risk(tmp_path: Path) -> None:
    parent = tmp_path / "public-parent-gitfile"
    init_repo(parent)
    common = tmp_path / "private-common.git"
    run_git(parent, "init", "--bare", str(common))
    nested = parent / "private-gitfile"
    nested.mkdir()
    (nested / ".git").write_text(f"gitdir: {common}\n")

    row = audit_one(parent, public_parent=True)

    assert row["nested_clone_count"] == 1
    assert row["nested_clones"] == [str(nested)]


def test_submodule_gitfile_inside_public_worktree_is_not_privacy_risk(tmp_path: Path) -> None:
    parent = tmp_path / "public-parent-submodule"
    init_repo(parent)
    nested = parent / "vendor-submodule"
    nested.mkdir()
    module_git = parent / ".git" / "modules" / "vendor-submodule"
    module_git.mkdir(parents=True)
    (nested / ".git").write_text(f"gitdir: {module_git}\n")

    row = audit_one(parent, public_parent=True)

    assert row["nested_clone_count"] == 0
    assert "PRIVACY-NESTED-CLONE" not in finding_codes(row)
