from __future__ import annotations

from pathlib import Path

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
                "workspace_root": r"D:\workspace-hub",
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
        resolver.rewrite_workspace_path(r"D:\workspace-hub\docs\report.md", current_repo_root=repo_root)
        == "docs/report.md"
    )
    assert (
        resolver.rewrite_workspace_path("/d/workspace-hub/docs/report.md", current_repo_root=repo_root)
        == "docs/report.md"
    )
    assert (
        resolver.rewrite_workspace_path("/D/workspace-hub/docs/report.md", current_repo_root=repo_root)
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
