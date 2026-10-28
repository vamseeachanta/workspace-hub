from __future__ import annotations

from pathlib import Path, PureWindowsPath

import pytest
import yaml

from workspace_hub.workstations.resolver import WorkstationPathResolver


def _write_registry(tmp_path: Path) -> Path:
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "hostname_aliases": ["vamsee-linux1"],
                "os": "linux",
                "workspace_root": "/mnt/local-analysis/workspace-hub",
                "ssh": "ace-linux-1",
            },
            "dev-secondary": {
                "hostname": "ace-linux-2",
                "hostname_aliases": [],
                "os": "linux",
                "workspace_root": "/mnt/workspace-hub",
                "ssh": "ssh-secondary",
            },
            "licensed-win-1": {
                "hostname": "licensed-win-1",
                "hostname_aliases": ["license-box"],
                "os": "windows",
                "workspace_root": r"C:\workspace-hub",
                "ssh": None,
            },
        }
    }
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
    return path


def test_resolve_machine_accepts_key_hostname_alias_and_ssh_target(tmp_path: Path) -> None:
    resolver = WorkstationPathResolver.from_registry_path(_write_registry(tmp_path))

    assert resolver.resolve_machine("dev-primary").key == "dev-primary"
    assert resolver.resolve_machine("ace-linux-1").key == "dev-primary"
    assert resolver.resolve_machine("vamsee-linux1").key == "dev-primary"
    assert resolver.resolve_machine("ssh-secondary").key == "dev-secondary"


def test_rewrite_workspace_path_normalizes_linux_and_windows_hosts(tmp_path: Path) -> None:
    resolver = WorkstationPathResolver.from_registry_path(_write_registry(tmp_path))
    repo_root = tmp_path / "worktree"

    assert (
        resolver.rewrite_workspace_path("/mnt/workspace-hub/docs/report.md", current_repo_root=repo_root)
        == "docs/report.md"
    )
    assert (
        resolver.rewrite_workspace_path(r"C:\workspace-hub\docs\report.md", current_repo_root=repo_root)
        == "docs/report.md"
    )
    assert (
        resolver.rewrite_workspace_path("/c/workspace-hub/docs/report.md", current_repo_root=repo_root)
        == "docs/report.md"
    )
    assert (
        resolver.rewrite_workspace_path("/C/workspace-hub/docs/report.md", current_repo_root=repo_root)
        == "docs/report.md"
    )


def test_rewrite_workspace_path_documents_current_non_anchored_matching(tmp_path: Path) -> None:
    resolver = WorkstationPathResolver.from_registry_path(_write_registry(tmp_path))

    assert (
        resolver.rewrite_workspace_path(
            "/mnt/workspace-hub/docs/report.md",
            current_repo_root=tmp_path / "different-checkout-name",
        )
        == "docs/report.md"
    )


def test_rewrite_workspace_path_falls_back_for_unknown_hosts(tmp_path: Path) -> None:
    resolver = WorkstationPathResolver.from_registry_path(_write_registry(tmp_path))
    repo_root = tmp_path / "worktree"

    assert (
        resolver.rewrite_workspace_path("/opt/external/shared/report.md", current_repo_root=repo_root)
        == "/opt/external/shared/report.md"
    )
    assert resolver.resolve_machine("unknown-host") is None


@pytest.fixture
def neutral_registry(tmp_path: Path) -> tuple[WorkstationPathResolver, dict[str, str]]:
    native_root = tmp_path / "source" / "checkout"
    windows_root = PureWindowsPath("Q:/") / tmp_path.name / "source" / "checkout"
    registry = {
        "machines": {
            "native": {"os": "linux", "workspace_root": str(native_root)},
            "windows": {"os": "windows", "workspace_root": str(windows_root)},
        }
    }
    registry_path = tmp_path / "neutral-registry.yaml"
    registry_path.write_text(yaml.safe_dump(registry), encoding="utf-8")
    roots = {
        "posix": str(native_root),
        "windows": str(windows_root),
        "msys-lower": f"/q/{tmp_path.name}/source/checkout",
        "msys-upper": f"/Q/{tmp_path.name}/source/checkout",
    }
    return WorkstationPathResolver.from_registry_path(registry_path), roots


@pytest.mark.parametrize("style", ["posix", "windows", "msys-lower", "msys-upper"])
def test_anchor_recognized_suffix(neutral_registry, tmp_path: Path, style: str) -> None:
    resolver, roots = neutral_registry
    repo_root = tmp_path / "selected-checkout"
    separator = "\\" if style == "windows" else "/"
    raw_path = separator.join((roots[style], "docs", "report.md"))
    # Expected location is hand-assembled from the checkout and literal components.
    expected = repo_root / "docs" / "report.md"

    assert resolver.rewrite_workspace_path(raw_path, repo_root, anchored=True) == str(expected)


@pytest.mark.parametrize("style", ["posix", "windows", "msys-lower", "msys-upper"])
def test_anchor_exact_root(neutral_registry, tmp_path: Path, style: str) -> None:
    resolver, roots = neutral_registry
    repo_root = tmp_path / "selected-checkout"

    assert resolver.rewrite_workspace_path(roots[style], repo_root, anchored=True) == str(repo_root)


@pytest.mark.parametrize("style", ["posix", "windows", "msys-lower", "msys-upper"])
@pytest.mark.parametrize("suffix", ["../outside", "docs/../../outside", r"docs\..\..\outside"])
def test_anchor_rejects_escape(neutral_registry, tmp_path: Path, style: str, suffix: str) -> None:
    resolver, roots = neutral_registry
    raw_path = roots[style] + "/" + suffix

    with pytest.raises(ValueError, match="escapes"):
        resolver.rewrite_workspace_path(raw_path, tmp_path / "selected-checkout", anchored=True)


@pytest.mark.parametrize("style", ["posix", "windows", "msys-lower", "msys-upper"])
def test_default_suffix_behavior_unchanged(neutral_registry, tmp_path: Path, style: str) -> None:
    resolver, roots = neutral_registry
    repo_root = tmp_path / "selected-checkout"

    assert resolver.rewrite_workspace_path(roots[style], repo_root) == "."
    for suffix in ("docs/report.md", "../outside"):
        raw_path = roots[style] + "/" + suffix
        assert resolver.rewrite_workspace_path(raw_path, repo_root) == suffix
        assert resolver.rewrite_workspace_path(raw_path, repo_root, anchored=False) == suffix


@pytest.mark.parametrize("raw_path", [None, "", "  ", "relative/../outside", "  unknown/report.md  "])
def test_anchor_preserves_unknown_and_empty_fallback(neutral_registry, tmp_path: Path, raw_path) -> None:
    resolver, _ = neutral_registry

    assert resolver.rewrite_workspace_path(raw_path, tmp_path, anchored=True) == (raw_path or "").strip()


def test_anchor_requires_root_component_boundary(neutral_registry, tmp_path: Path) -> None:
    resolver, roots = neutral_registry
    raw_path = roots["posix"] + "-other/docs/report.md"

    assert resolver.rewrite_workspace_path(raw_path, tmp_path, anchored=True) == raw_path


def test_anchor_rejects_symlink_escape(neutral_registry, tmp_path: Path) -> None:
    resolver, roots = neutral_registry
    repo_root = tmp_path / "selected-checkout"
    repo_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo_root / "redirect").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="escapes"):
        resolver.rewrite_workspace_path(roots["posix"] + "/redirect/report.md", repo_root, anchored=True)


def test_anchor_resolves_relative_checkout_and_internal_traversal(neutral_registry, tmp_path: Path, monkeypatch) -> None:
    resolver, roots = neutral_registry
    monkeypatch.chdir(tmp_path)
    raw_path = roots["posix"] + "/docs/../report.md"
    expected = tmp_path / "selected-checkout" / "report.md"

    assert resolver.rewrite_workspace_path(raw_path, Path("selected-checkout"), anchored=True) == str(expected)
