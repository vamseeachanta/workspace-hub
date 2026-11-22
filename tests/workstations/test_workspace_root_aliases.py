"""Synthetic examples of additive workspace root matching.

Expected suffixes are derived by hand: remove the declared root and its next
separator, keeping the remaining path components. Unmatched paths stay intact.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from workspace_hub.workstations.resolver import WorkstationPathResolver


def _resolver(tmp_path: Path, record: dict[str, object]) -> WorkstationPathResolver:
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump({"machines": {"workstation": record}}), encoding="utf-8"
    )
    return WorkstationPathResolver.from_registry_path(registry)


def test_declared_workspace_root_alias_rewrites_suffix(tmp_path: Path) -> None:
    root = tmp_path / "canonical"
    alias = tmp_path / "alternate"
    resolver = _resolver(
        tmp_path,
        {"os": "linux", "workspace_root": str(root), "workspace_root_aliases": [str(alias)]},
    )

    for declared in (alias, root):
        assert (
            resolver.rewrite_workspace_path(str(declared / "docs" / "report.md"), tmp_path)
            == "docs/report.md"
        )


def test_aliases_with_spaces_and_trailing_separators(tmp_path: Path) -> None:
    alias = tmp_path / "alternate workspace"
    other_alias = tmp_path / "another workspace"
    resolver = _resolver(
        tmp_path,
        {
            "os": "linux",
            "workspace_root": str(tmp_path / "canonical"),
            "workspace_root_aliases": [f"  {alias}/  ", str(other_alias)],
        },
    )

    for declared in (alias, other_alias):
        assert (
            resolver.rewrite_workspace_path(str(declared / "docs" / "report.md"), tmp_path)
            == "docs/report.md"
        )
        assert resolver.rewrite_workspace_path(str(declared), tmp_path) == "."
        assert resolver.rewrite_workspace_path(f"{declared}/", tmp_path) == "."


def test_alias_equal_to_canonical_root(tmp_path: Path) -> None:
    root = tmp_path / "canonical"
    resolver = _resolver(
        tmp_path,
        {
            "os": "linux",
            "workspace_root": str(root),
            "workspace_root_aliases": [str(root), f"{root}/", str(root)],
        },
    )

    assert resolver.rewrite_workspace_path(str(root), tmp_path) == "."
    assert resolver.rewrite_workspace_path(str(root / "docs"), tmp_path) == "docs"


def test_alias_prefix_requires_component_boundary(tmp_path: Path) -> None:
    alias = tmp_path / "alternate"
    resolver = _resolver(
        tmp_path,
        {
            "os": "linux",
            "workspace_root": str(tmp_path / "canonical"),
            "workspace_root_aliases": [str(alias)],
        },
    )

    for unrelated in (
        f"{alias}-copy/docs",
        f"{alias}extra/docs",
        str(tmp_path / "Alternate" / "docs"),
    ):
        assert resolver.rewrite_workspace_path(unrelated, tmp_path) == unrelated
    assert resolver.rewrite_workspace_path(str(alias / "docs"), tmp_path) == "docs"


@pytest.mark.parametrize("alias", [r"D:\alternate workspace", "D:/alternate workspace/"])
@pytest.mark.parametrize(
    "raw_path",
    [
        r"D:\alternate workspace\Docs\Report.md",
        "d:/alternate workspace/Docs/Report.md",
        "D://alternate workspace//Docs//Report.md",
        "/d/alternate workspace/Docs/Report.md",
        "/D/alternate workspace/Docs/Report.md",
    ],
)
def test_alias_windows_forms(tmp_path: Path, alias: str, raw_path: str) -> None:
    resolver = _resolver(
        tmp_path,
        {"os": "windows", "workspace_root": "C:/canonical", "workspace_root_aliases": [alias]},
    )

    assert resolver.rewrite_workspace_path(raw_path, tmp_path) == "Docs/Report.md"
    assert resolver.rewrite_workspace_path(alias, tmp_path) == "."
    assert (
        resolver.rewrite_workspace_path("C:/canonical/Docs/Report.md", tmp_path)
        == "Docs/Report.md"
    )
    unrelated = "D:/alternate workspace-copy/Docs/Report.md"
    assert resolver.rewrite_workspace_path(unrelated, tmp_path) == unrelated


def test_missing_aliases_preserve_existing_behavior(tmp_path: Path) -> None:
    root = tmp_path / "canonical"
    resolver = _resolver(tmp_path, {"os": "linux", "workspace_root": str(root)})
    unrelated = str(tmp_path / "alternate" / "docs")

    assert resolver.rewrite_workspace_path(str(root / "docs"), tmp_path) == "docs"
    assert resolver.rewrite_workspace_path(str(root), tmp_path) == "."
    assert resolver.rewrite_workspace_path(unrelated, tmp_path) == unrelated
    assert resolver.rewrite_workspace_path(f"{root}-copy/docs", tmp_path) == f"{root}-copy/docs"
    assert resolver.rewrite_workspace_path(None, tmp_path) == ""


@pytest.mark.parametrize("invalid_kind", ["null", "string", "mapping", "boolean", "tuple"])
def test_invalid_alias_field_types_are_ignored(tmp_path: Path, invalid_kind: str) -> None:
    root = tmp_path / "canonical"
    alias = tmp_path / "alternate"
    invalid_fields = {
        "null": None,
        "string": str(alias),
        "mapping": {str(alias): "ignored"},
        "boolean": False,
        "tuple": (str(alias),),
    }
    resolver = _resolver(tmp_path, {"os": "linux", "workspace_root": str(root)})
    # Set after YAML loading so the tuple is not serialized as a valid list.
    machine = resolver.resolve_machine("workstation")
    assert machine is not None
    machine.raw["workspace_root_aliases"] = invalid_fields[invalid_kind]

    assert resolver.rewrite_workspace_path(str(root / "docs"), tmp_path) == "docs"
    assert resolver.rewrite_workspace_path(str(alias / "docs"), tmp_path) == str(alias / "docs")


def test_invalid_alias_elements_are_ignored(tmp_path: Path) -> None:
    alias = tmp_path / "alternate"
    resolver = _resolver(
        tmp_path,
        {
            "os": "linux",
            "workspace_root": str(tmp_path / "canonical"),
            "workspace_root_aliases": [None, False, {}, [], "", "  ", str(alias)],
        },
    )

    assert resolver.rewrite_workspace_path(str(alias / "docs"), tmp_path) == "docs"
    for unrelated in ("False/docs", "None/docs", "{}/docs", "[]/docs", "/docs"):
        assert resolver.rewrite_workspace_path(unrelated, tmp_path) == unrelated


def test_canonical_root_matches_before_nested_alias(tmp_path: Path) -> None:
    root = tmp_path / "canonical"
    resolver = _resolver(
        tmp_path,
        {
            "os": "linux",
            "workspace_root": str(root),
            "workspace_root_aliases": [str(root / "nested")],
        },
    )

    assert (
        resolver.rewrite_workspace_path(str(root / "nested" / "docs"), tmp_path)
        == "nested/docs"
    )
