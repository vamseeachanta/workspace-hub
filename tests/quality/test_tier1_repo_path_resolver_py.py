from pathlib import Path

import pytest

from scripts.lib.tier1_repos import resolve_tier1_repo_path


def _repo_marker(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")


def test_resolves_nested_repo_first(tmp_path: Path) -> None:
    hub = tmp_path / "workspace-hub"
    nested = hub / "assetutilities"
    sibling = tmp_path / "assetutilities"
    _repo_marker(nested)
    _repo_marker(sibling)

    assert resolve_tier1_repo_path("assetutilities", repo_root=hub) == nested


def test_resolves_sibling_repo_when_nested_absent(tmp_path: Path) -> None:
    hub = tmp_path / "workspace-hub"
    sibling = tmp_path / "assetutilities"
    hub.mkdir()
    _repo_marker(sibling)

    assert resolve_tier1_repo_path("assetutilities", repo_root=hub) == sibling


def test_explicit_base_precedes_nested_and_sibling(tmp_path: Path) -> None:
    hub = tmp_path / "workspace-hub"
    base = tmp_path / "external"
    based = base / "assetutilities"
    nested = hub / "assetutilities"
    sibling = tmp_path / "assetutilities"
    _repo_marker(based)
    _repo_marker(nested)
    _repo_marker(sibling)

    assert resolve_tier1_repo_path("assetutilities", repo_root=hub, base=base) == based


def test_missing_repo_fails_closed(tmp_path: Path) -> None:
    hub = tmp_path / "workspace-hub"
    hub.mkdir()

    with pytest.raises(FileNotFoundError):
        resolve_tier1_repo_path("assetutilities", repo_root=hub)


def _git(cwd, *args):
    """Mutate only disposable fixtures; ignore inherited Git bindings."""
    import os
    import subprocess

    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(cwd), *args], env=env,
        check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.fixture
def linked_layout(tmp_path, monkeypatch):
    """Git's commondir layout supplies the canonical root, at any depth."""
    for name in ("REPO_ROOT", "TIER1_REPOS_BASE"):
        monkeypatch.delenv(name, raising=False)
    canonical = tmp_path / "workspace" / "hub"
    canonical.mkdir(parents=True)
    _git(canonical, "init")
    linked = tmp_path / "worktrees" / "nested" / "deeper" / "hub"
    _git(canonical, "worktree", "add", "--orphan", "-b", "fixture-branch", str(linked))
    return canonical, linked


def test_linked_worktree_resolves_canonical_sibling(linked_layout):
    canonical, linked = linked_layout
    sibling = canonical.parent / "fixture-repo"
    _repo_marker(sibling)
    assert resolve_tier1_repo_path("fixture-repo", repo_root=canonical) == sibling
    assert resolve_tier1_repo_path("fixture-repo", repo_root=linked) == sibling


def test_linked_worktree_resolves_canonical_nested_repo(linked_layout):
    canonical, linked = linked_layout
    nested = canonical / "fixture-repo"
    _repo_marker(nested)
    assert resolve_tier1_repo_path("fixture-repo", repo_root=linked) == nested


def test_current_layout_precedes_canonical_fallback(linked_layout):
    canonical, linked = linked_layout
    _repo_marker(canonical / "fixture-repo")
    local = linked / "fixture-repo"
    _repo_marker(local)
    assert resolve_tier1_repo_path("fixture-repo", repo_root=linked) == local


def test_linked_marker_without_pyproject(tmp_path):
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    _git(canonical, "init")
    linked = tmp_path / "hub" / "fixture-repo"
    _git(canonical, "worktree", "add", "--orphan", "-b", "fixture-branch", str(linked))
    assert resolve_tier1_repo_path("fixture-repo", repo_root=linked.parent) == linked


def test_git_bindings_cannot_redirect_canonical_fallback(linked_layout, tmp_path, monkeypatch):
    canonical, linked = linked_layout
    sibling = canonical.parent / "fixture-repo"
    _repo_marker(sibling)
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    monkeypatch.setenv("GIT_COMMON_DIR", str(other / ".git"))
    assert resolve_tier1_repo_path("fixture-repo", repo_root=linked) == sibling


def test_missing_sibling_in_linked_layout_fails_closed(linked_layout):
    _, linked = linked_layout
    with pytest.raises(FileNotFoundError):
        resolve_tier1_repo_path("absent-repo", repo_root=linked)
