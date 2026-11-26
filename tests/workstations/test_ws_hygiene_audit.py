"""Tests for scripts/workstations/ws_hygiene_audit.py and ws-root-policy.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts" / "workstations"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import ws_hygiene_audit as audit  # noqa: E402


def _make_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    (repo / ".git" / "worktrees").mkdir(parents=True)
    return repo


def _make_linked_wt(repo: Path, wt_parent: Path, name: str, broken: bool = False) -> Path:
    wt = wt_parent / name
    wt.mkdir(parents=True)
    gitdir = repo / ".git" / "worktrees" / name
    if not broken:
        gitdir.mkdir(parents=True)
    (wt / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
    return wt


def test_default_policy_loads_cleanly() -> None:
    policy = audit.load_policy()
    assert policy["schema_version"] == 1
    assert {"_wt", "_pm", "_backups", "_archive", "_scratch"} <= set(policy["reserved_system_dirs"])
    assert policy["root_rules"]["allow_loose_files"] is False


def test_clean_workspace_is_compliant(tmp_path: Path) -> None:
    policy = audit.load_policy()
    repo = _make_repo(tmp_path, "sample-repo")
    for reserved in ("_wt", "_pm", "_backups", "_archive", ".claude"):
        (tmp_path / reserved).mkdir()
    _make_linked_wt(repo, tmp_path / "_wt", "sample-repo-fix")

    report = audit.audit_workspace_root(tmp_path, policy)
    assert report["compliant"] is True
    assert report["git_repos"] == ["sample-repo"]
    assert report["wt_linked_count"] == 1
    assert report["total_violations"] == 0


def test_detects_root_and_wt_violations(tmp_path: Path) -> None:
    policy = audit.load_policy()
    repo = _make_repo(tmp_path, "sample-repo")
    wt_dir = tmp_path / "_wt"
    wt_dir.mkdir()

    # Root violations
    (tmp_path / "stray.md").write_text("oops", encoding="utf-8")
    (tmp_path / "random-folder").mkdir()
    (tmp_path / "sample-repo.pre-rollout-2026-11-23").mkdir()
    _make_linked_wt(repo, tmp_path, "root-wt")

    # _wt violations
    (wt_dir / "note.txt").write_text("stray", encoding="utf-8")
    (wt_dir / "scratch-dir").mkdir()
    _make_repo(wt_dir, "standalone-clone")
    _make_linked_wt(repo, wt_dir, "broken-wt", broken=True)

    report = audit.audit_workspace_root(tmp_path, policy)
    assert report["compliant"] is False
    root_kinds = {v["name"]: v["kind"] for v in report["root_violations"]}
    assert root_kinds["stray.md"] == "loose_root_file"
    assert root_kinds["random-folder"] == "non_git_root_dir"
    assert root_kinds["sample-repo.pre-rollout-2026-11-23"] == "forbidden_root_pattern"
    assert root_kinds["root-wt"] == "worktree_at_root"

    wt_kinds = {v["name"]: v["kind"] for v in report["wt_violations"]}
    assert wt_kinds["note.txt"] == "loose_file_in_wt"
    assert wt_kinds["scratch-dir"] == "non_git_dir_in_wt"
    assert wt_kinds["standalone-clone"] == "standalone_clone_in_wt"
    assert wt_kinds["broken-wt"] == "broken_worktree_gitdir"


def test_allow_extra_dir_and_strict_exit_code(tmp_path: Path) -> None:
    _make_repo(tmp_path, "repo-a")
    (tmp_path / "runtime-dir").mkdir()

    rc_fail = audit.main(["--root", str(tmp_path), "--strict"])
    assert rc_fail == 1

    rc_pass = audit.main(["--root", str(tmp_path), "--allow-extra-dir", "runtime-dir", "--strict"])
    assert rc_pass == 0
