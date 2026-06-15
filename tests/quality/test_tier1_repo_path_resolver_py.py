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
