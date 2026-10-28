"""Synthetic golden cases for text normalization, never storage qualification.

Expected strings are hand-derived from the acceptance contract: remove a whole
registered root and its boundary separator, or preserve unresolved input text.
Braced fields supply temporary roots only; expected suffixes remain literals.
No rewritten value establishes existence, checkout membership, or ownership.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath

import pytest
import yaml

from workspace_hub.workstations.resolver import WorkstationPathResolver


def fixture_roots(tmp_path: PurePath) -> dict[str, str]:
    # Strip the native anchor before adding the synthetic drive and aliases.
    drive_tail = PurePosixPath("/", *tmp_path.relative_to(tmp_path.anchor).parts, "drive")
    return {
        "registered": (tmp_path / "registered").as_posix(),
        "alias": (tmp_path / "alias").as_posix(),
        "external": (tmp_path / "external").as_posix(),
        "drive_tail": drive_tail.as_posix(),
        "drive_backslashes": drive_tail.as_posix().replace("/", "\\"),
    }


@pytest.fixture
def roots(tmp_path: Path, request: pytest.FixtureRequest) -> dict[str, str]:
    return fixture_roots(getattr(request, "param", tmp_path))


@pytest.fixture
def rewrite(
    tmp_path: Path, roots: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> Callable[[str | None], str]:
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "machines": {
                    "synthetic-posix": {
                        "os": "linux",
                        "workspace_root": roots["registered"],
                    },
                    "synthetic-alias": {
                        "os": "linux",
                        "workspace_root": roots["alias"],
                    },
                    "synthetic-drive": {
                        "os": "windows",
                        "workspace_root": "R:" + roots["drive_backslashes"],
                    },
                }
            }
        ),
        encoding="utf-8",
        newline="\n",
    )
    resolver = WorkstationPathResolver.from_registry_path(registry_path)
    current_root = tmp_path / "unrelated-checkout"
    # A defined variable would expose accidental symbolic expansion.
    monkeypatch.setenv("WORKSPACE_ROOT", roots["registered"])

    def forbidden_probe(*args: object, **kwargs: object) -> None:
        raise AssertionError("Normalization must not inspect storage")

    def resolve_current_root(path: Path, *args: object, **kwargs: object) -> Path:
        # Permit the existing current-root canonicalization without disk access.
        # Any attempt to resolve an input or rewritten descendant still fails.
        assert path == current_root
        return current_root

    def rewrite_text(raw: str | None) -> str:
        # Scope the guard to the resolver, so pytest can manage its own files.
        with monkeypatch.context() as guard:
            guard.setattr(Path, "resolve", resolve_current_root)
            for method in ("exists", "is_file", "is_dir", "is_symlink", "open"):
                guard.setattr(Path, method, forbidden_probe)
            for method in ("exists", "lexists", "isfile", "isdir", "islink"):
                guard.setattr(os.path, method, forbidden_probe)
            for method in ("stat", "lstat", "scandir", "access"):
                guard.setattr(os, method, forbidden_probe)
            return resolver.rewrite_workspace_path(raw, current_repo_root=current_root)

    return rewrite_text


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(None, "", id="unresolved-none-is-empty"),
        pytest.param("", "", id="unresolved-empty"),
        pytest.param(" \t ", "", id="unresolved-blank-is-empty"),
        pytest.param("{registered}", ".", id="normalized-exact-root"),
        pytest.param("{registered}/", ".", id="normalized-root-trailing-separator"),
        pytest.param("{alias}", ".", id="normalized-alias-root"),
        pytest.param("R:{drive_tail}", ".", id="normalized-drive-root"),
        pytest.param("R:{drive_backslashes}", ".", id="normalized-backslash-drive-root"),
    ],
)
def test_exact_root_and_empty_input(
    raw: str | None,
    expected: str,
    roots: dict[str, str],
    rewrite: Callable[[str | None], str],
) -> None:
    """Empty input stays empty; a registered root denotes only the lexical dot."""
    assert rewrite(raw.format_map(roots) if raw is not None else None) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(
            "{registered}-other/docs/report.md",
            "{registered}-other/docs/report.md",
            id="unresolved-posix-prefix-lookalike",
        ),
        pytest.param(
            "R:{drive_tail}-other/docs/report.md",
            "R:{drive_tail}-other/docs/report.md",
            id="unresolved-drive-prefix-lookalike",
        ),
        pytest.param(
            "{external}/docs/report.md",
            "{external}/docs/report.md",
            id="unresolved-external-read",
        ),
        pytest.param(
            "{external}//docs///report.md",
            "{external}//docs///report.md",
            id="unresolved-external-separators-preserved",
        ),
    ],
)
def test_prefix_lookalike_not_rewritten(
    raw: str,
    expected: str,
    roots: dict[str, str],
    rewrite: Callable[[str | None], str],
) -> None:
    """A textual prefix alone supplies no registered-root boundary or ownership."""
    assert rewrite(raw.format_map(roots)) == expected.format_map(roots)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(
            "{registered}/absent/nested/report.md",
            "absent/nested/report.md",
            id="normalized-registered-missing-descendant",
        ),
        pytest.param(
            "{alias}/absent/nested/report.md",
            "absent/nested/report.md",
            id="normalized-alias-missing-descendant",
        ),
    ],
)
def test_missing_descendant_is_only_normalized(
    raw: str,
    expected: str,
    tmp_path: Path,
    roots: dict[str, str],
    rewrite: Callable[[str | None], str],
) -> None:
    """Independent absence checks surround rewriting, which cannot probe storage."""
    source = raw.format_map(roots)
    destination = tmp_path / "unrelated-checkout" / expected
    assert not Path(source).exists()
    assert not destination.exists()
    assert rewrite(source) == expected
    assert not Path(source).exists()
    assert not destination.exists()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(
            "$WORKSPACE_ROOT/docs/report.md",
            "$WORKSPACE_ROOT/docs/report.md",
            id="unresolved-variable",
        ),
        pytest.param(
            "${WORKSPACE_ROOT}/docs/report.md",
            "${WORKSPACE_ROOT}/docs/report.md",
            id="unresolved-braced-variable",
        ),
        pytest.param("~/docs/report.md", "~/docs/report.md", id="unresolved-tilde"),
        pytest.param(
            "workspace://docs/report.md",
            "workspace://docs/report.md",
            id="unresolved-symbolic-uri",
        ),
        pytest.param(
            r"external\docs\report.md",
            r"external\docs\report.md",
            id="unresolved-relative-backslashes",
        ),
    ],
)
def test_symbolic_text_remains_text(
    raw: str, expected: str, rewrite: Callable[[str | None], str]
) -> None:
    """Symbols and unknown paths remain literal; no expansion or access is implied."""
    assert rewrite(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("R:{drive_tail}/docs/report.md", "docs/report.md", id="normalized-drive-upper"),
        pytest.param("r:{drive_tail}/docs/report.md", "docs/report.md", id="normalized-drive-lower"),
        pytest.param(
            r"R:{drive_backslashes}\docs\report.md",
            "docs/report.md",
            id="normalized-backslash-separators",
        ),
        pytest.param(
            "R:{drive_tail}\\docs\\report.md", "docs/report.md", id="normalized-mixed-separators"
        ),
        pytest.param(
            "R:{drive_tail}//docs///report.md", "docs/report.md", id="normalized-repeated-separators"
        ),
        pytest.param(
            "/r{drive_tail}/docs/report.md", "docs/report.md", id="normalized-drive-alias-lower"
        ),
        pytest.param(
            "/R{drive_tail}/docs/report.md", "docs/report.md", id="normalized-drive-alias-upper"
        ),
    ],
)
def test_drive_letter_casing_and_separator_variants(
    raw: str,
    expected: str,
    roots: dict[str, str],
    rewrite: Callable[[str | None], str],
) -> None:
    """Drive aliases normalize to a literal suffix without asserting access."""
    assert rewrite(raw.format_map(roots)) == expected


@pytest.mark.parametrize("roots", [PureWindowsPath("Q:/temporary/coherence")], indirect=True)
@pytest.mark.parametrize("alias", ["r", "R"])
def test_native_windows_temporary_root_drive_aliases(
    alias: str, roots: dict[str, str], rewrite: Callable[[str | None], str]
) -> None:
    """Native temporary drives must not become part of synthetic drive tails."""
    assert rewrite(f"/{alias}{roots['drive_tail']}/docs/report.md") == "docs/report.md"
    assert roots["drive_tail"] == "/temporary/coherence/drive"
