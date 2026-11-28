"""Tests for scripts/workstations/ws_hygiene_audit.py and ws-root-policy.yaml."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts" / "workstations"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import ws_hygiene_audit as audit  # noqa: E402


def _git(*args: str | Path) -> None:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    subprocess.run(
        ["git", *args], env=env, check=True, capture_output=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def _make_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    _git("init", repo)
    _git("-C", repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
         "commit", "--allow-empty", "-m", "Fixture base")
    return repo


def _make_linked_wt(repo: Path, wt_parent: Path, name: str) -> Path:
    wt = wt_parent / name
    _git("-C", repo, "worktree", "add", "--detach", wt)
    return wt


def test_default_policy_loads_cleanly() -> None:
    policy = audit.load_policy()
    assert policy["schema_version"] == 1
    assert {"_wt", "_pm", "_backups", "_archive"} == set(policy["reserved_system_dirs"])
    assert policy["root_rules"]["allow_loose_files"] is False


def test_clean_workspace_is_compliant(tmp_path: Path) -> None:
    policy = audit.load_policy()
    repo = _make_repo(tmp_path, "workspace-hub")
    for reserved in ("_wt", "_pm", "_backups", "_archive", ".claude"):
        (tmp_path / reserved).mkdir()
    _make_linked_wt(repo, tmp_path / "_wt", "sample--fix")

    report = audit.audit_workspace_root(tmp_path, policy)
    assert report["compliant"] is True
    assert report["git_repos"] == ["workspace-hub"]
    assert report["wt_linked_count"] == 1
    assert report["total_violations"] == 0


def test_detects_root_and_wt_violations(tmp_path: Path) -> None:
    policy = audit.load_policy()
    repo = _make_repo(tmp_path, "workspace-hub")
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
    broken = wt_dir / "broken-wt"
    broken.mkdir()
    (broken / ".git").write_text("gitdir: missing\n", encoding="utf-8")

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
    _make_repo(tmp_path, "workspace-hub")
    (tmp_path / "runtime-dir").mkdir()

    rc_fail = audit.main(["--root", str(tmp_path), "--strict"])
    assert rc_fail == 1

    rc_pass = audit.main(["--root", str(tmp_path), "--allow-extra-dir", "runtime-dir", "--strict"])
    assert rc_pass == 0


def test_rejects_external_gitdir_and_mismatched_backlink_in_wt(tmp_path: Path) -> None:
    policy = audit.load_policy()
    repo = _make_repo(tmp_path, "workspace-hub")
    wt_dir = tmp_path / "_wt"
    wt_dir.mkdir()

    # External standalone .git directory (no commondir/backlink)
    external_clone = wt_dir / "external-gitdir-clone"
    external_clone.mkdir()
    (external_clone / ".git").write_text(f"gitdir: {repo / '.git'}\n", encoding="utf-8")

    # Worktree admin dir whose backlink points elsewhere
    wrong_backlink = wt_dir / "wrong-backlink-wt"
    wrong_backlink.mkdir()
    admin_dir = repo / ".git" / "worktrees" / "wrong-backlink-wt"
    admin_dir.mkdir(parents=True)
    (admin_dir / "commondir").write_text("../..\n", encoding="utf-8")
    (admin_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (admin_dir / "gitdir").write_text(f"{wt_dir / 'other' / '.git'}\n", encoding="utf-8")
    (wrong_backlink / ".git").write_text(f"gitdir: {admin_dir}\n", encoding="utf-8")

    report = audit.audit_workspace_root(tmp_path, policy)
    assert report["compliant"] is False
    wt_kinds = {v["name"]: v["kind"] for v in report["wt_violations"]}
    assert wt_kinds["external-gitdir-clone"] == "not_linked_worktree_gitdir"
    assert wt_kinds["wrong-backlink-wt"] == "invalid_worktree_backlink"


def test_incomplete_repository_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _make_repo(tmp_path, "valid")
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    wt = tmp_path / "_wt" / "incomplete"
    wt.mkdir(parents=True)
    admin = tmp_path / "_scratch" / "admin"
    admin.mkdir(parents=True)
    marker = wt / ".git"
    marker.write_text(f"gitdir: {admin}\n", encoding="utf-8")
    (admin / "gitdir").write_text(f"{marker}\n", encoding="utf-8")
    (admin / "commondir").write_text("..\n", encoding="utf-8")
    (admin / "HEAD").touch()

    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    assert report["wt_linked_count"] == 0
    assert report["wt_violations"][0]["kind"] == "incomplete_worktree_metadata"
    assert audit.main(["--root", str(tmp_path), "--strict"]) == 1


@pytest.mark.parametrize("link_at_root", [False, True], ids=["worktree-entry", "reserved-root"])
def test_external_directory_link(tmp_path: Path, link_at_root: bool) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    repo = _make_repo(root, "workspace-hub")
    external = tmp_path / "external"
    external.mkdir()
    checkout = _make_linked_wt(repo, external, "real")
    wt_dir = root / "_wt"
    if link_at_root:
        link, target = wt_dir, external
    else:
        wt_dir.mkdir()
        link, target = wt_dir / "alias", checkout
    if os.name == "nt":
        subprocess.run(["cmd", "/d", "/c", "mklink", "/J", link, target], check=True)
    else:
        link.symlink_to(target, target_is_directory=True)

    report = audit.audit_workspace_root(root, audit.load_policy())
    assert report["wt_linked_count"] == 0
    assert report["total_violations"] == 1
    violations = report["root_violations"] if link_at_root else report["wt_violations"]
    assert violations[0]["name"] == link.name
    assert audit.main(["--root", str(root), "--strict"]) == 1


def test_scratch_and_unregistered_repository_are_findings(tmp_path: Path) -> None:
    policy = audit.load_policy()
    policy["registered_repositories"] = ["known"]
    _make_repo(tmp_path, "known")
    _make_repo(tmp_path, "unknown")
    (tmp_path / "_scratch").mkdir()
    report = audit.audit_workspace_root(tmp_path, policy, allow_extra_dirs=["_scratch"])
    assert report["git_repos"] == ["known"]
    assert {v["name"]: v["kind"] for v in report["root_violations"]} == {
        "_scratch": "forbidden_root_pattern", "unknown": "unregistered_repository",
    }


@pytest.mark.parametrize("scope", ["root", "_wt"])
def test_symlinked_git_marker(tmp_path: Path, scope: str, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _make_repo(tmp_path, "workspace-hub")
    wt_dir = tmp_path / "_wt"
    wt_dir.mkdir()
    parent = tmp_path if scope == "root" else wt_dir
    checkout = _make_linked_wt(repo, parent, "repo--linked")
    marker = checkout / ".git"
    target = repo / ".git" / "test-marker"
    marker.rename(target)
    try:
        marker.symlink_to(target)
    except OSError as exc:
        if getattr(exc, "winerror", None) != 1314:
            raise
        # Windows without symlink privilege: simulate only the marker type.
        target.rename(marker)
        original = Path.is_symlink
        monkeypatch.setattr(Path, "is_symlink", lambda path: path == marker or original(path))
    original_read = Path.read_text

    def read_text(path, *args, **kwargs):
        assert path != marker, "audit followed the linked marker"
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    findings = report["root_violations"] if scope == "root" else report["wt_violations"]
    assert [v["kind"] for v in findings] == ["symlinked_git_marker"]


@pytest.mark.parametrize("scope", ["root", "_wt"])
@pytest.mark.parametrize("operation", ["iterdir", "is_symlink"])
def test_permission_error_is_a_finding(tmp_path, monkeypatch, scope, operation):
    directory = tmp_path if scope == "root" else tmp_path / "_wt"
    directory.mkdir(exist_ok=True)
    blocked = directory if operation == "iterdir" else directory / "blocked"
    blocked.mkdir(exist_ok=True)
    original = getattr(Path, operation)

    def deny_access(path):
        if path == blocked:
            raise PermissionError()
        return original(path)

    monkeypatch.setattr(Path, operation, deny_access)
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    findings = report["root_violations"] if scope == "root" else report["wt_violations"]
    assert [(v["name"], v["kind"]) for v in findings] == [(blocked.name, "permission_denied")]


def test_git_timeout_is_a_finding(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path, "workspace-hub")
    wt_dir = tmp_path / "_wt"
    wt_dir.mkdir()
    _make_linked_wt(repo, wt_dir, "repo--fix")

    def timeout(args, **kwargs):
        assert kwargs["timeout"] > 0
        raise subprocess.TimeoutExpired(args, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timeout)
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    assert report["wt_violations"][0]["kind"] == "git_verification_timeout"


def test_linked_worktree_name_requires_double_separator(tmp_path):
    repo = _make_repo(tmp_path, "workspace-hub")
    wt_dir = tmp_path / "_wt"
    wt_dir.mkdir()
    _make_linked_wt(repo, wt_dir, "repo-fix")
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    assert report["wt_violations"][0]["kind"] == "invalid_worktree_name"


def test_workspace_root_alias_is_not_traversed(tmp_path, monkeypatch):
    root = tmp_path / "alias"
    target = tmp_path / "registered"
    target.mkdir()
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/d", "/c", "mklink", "/J", root, target], check=True,
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW,
        )
    else:
        root.symlink_to(target, target_is_directory=True)
    monkeypatch.setattr(Path, "iterdir", lambda path: pytest.fail("root alias was traversed"))
    report = audit.audit_workspace_root(root, audit.load_policy())
    assert report["root_violations"][0]["kind"] == "workspace_root_alias"


def test_empty_git_directory(tmp_path, monkeypatch):
    parent = _make_repo(tmp_path, "parent")
    root = parent / "workspace"
    (root / "workspace-hub" / ".git").mkdir(parents=True)
    monkeypatch.setenv("GIT_DIR", str(parent / ".git"))
    report = audit.audit_workspace_root(root, audit.load_policy())
    assert report["git_repos"] == []
    assert report["root_violations"][0]["name"] == "workspace-hub"
    assert audit.main(["--root", str(root), "--strict"]) == 1


@pytest.mark.parametrize("native", [
    False, pytest.param(True, marks=pytest.mark.skipif(os.name != "nt", reason="Windows junction")),
])
def test_git_marker_junction(tmp_path, monkeypatch, native):
    from types import SimpleNamespace

    root = tmp_path / "workspace"
    root.mkdir()
    marker = root / "workspace-hub" / ".git"
    if native:
        marker.parent.mkdir()
        target = _make_repo(tmp_path, "external") / ".git"
        subprocess.run(["cmd", "/d", "/c", "mklink", "/J", marker, target], check=True,
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        _make_repo(root, "workspace-hub")
        original = Path.lstat

        def lstat(path):
            info = original(path)
            if path == marker:
                return SimpleNamespace(st_mode=info.st_mode,
                                       st_file_attributes=audit.stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return info

        monkeypatch.setattr(Path, "lstat", lstat)
    report = audit.audit_workspace_root(root, audit.load_policy())
    assert report["git_repos"] == []
    assert report["root_violations"][0]["kind"] == "symlinked_git_marker"


def test_unlisted_worktree_metadata(tmp_path):
    repo = _make_repo(tmp_path, "workspace-hub")
    wt = _make_linked_wt(repo, tmp_path / "_wt", "repo--fix")
    admin = repo / ".git" / "worktrees" / wt.name
    moved = repo / ".git" / "rescue" / wt.name
    moved.parent.mkdir()
    admin.rename(moved)
    (wt / ".git").write_text(f"gitdir: {moved}\n", encoding="utf-8")
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    assert report["wt_linked_count"] == 0
    assert report["wt_violations"][0]["kind"] == "unregistered_worktree"


def test_nul_gitdir_preserves_sibling_finding(tmp_path):
    checkout = tmp_path / "_wt" / "broken"
    checkout.mkdir(parents=True)
    (checkout / ".git").write_bytes(b"gitdir: bad\0path\n")
    (checkout.parent / "stray.txt").touch()
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    assert {v["name"]: v["kind"] for v in report["wt_violations"]} == {
        "broken": "malformed_git_file", "stray.txt": "loose_file_in_wt",
    }


@pytest.mark.skipif(os.name == "nt", reason="POSIX FIFO")
@pytest.mark.parametrize("name", ["_wt", "_pm"])
def test_reserved_fifo(tmp_path, name):
    os.mkfifo(tmp_path / name)
    report = audit.audit_workspace_root(tmp_path, audit.load_policy())
    assert report["reserved_dirs_present"] == []
    assert report["root_violations"][0]["name"] == name
