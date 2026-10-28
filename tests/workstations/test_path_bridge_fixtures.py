"""Synthetic examples for the shipped resolver subset; no launcher is exercised.

Expected suffixes are hand calculations: remove the declared workspace prefix
and its following separator, then spell the remaining components with slashes.
The literal suffixes below are independent of resolver helpers. Drive letters,
share components and filenames are arbitrary fixture labels, not real locations.
Extend cases with a literal expectation and its derivation; do not infer results
from the resolver, a registry, an installed Git executable or cygpath.
"""
from __future__ import annotations

from collections.abc import Callable, Iterator
from copy import deepcopy
from pathlib import Path

import pytest

from workspace_hub.workstations.resolver import MachineRecord, WorkstationPathResolver


@pytest.fixture
def resolver_factory(tmp_path: Path) -> Iterator[Callable[..., WorkstationPathResolver]]:
    """Keep registry records, source bytes and caller metadata unchanged."""
    source = tmp_path / "source" / "docs"
    source.mkdir(parents=True)
    (source / "guide.md").write_text("synthetic source\n", encoding="utf-8")
    metadata = tmp_path / "checkout" / ".git"
    metadata.mkdir(parents=True)
    (metadata / "config").write_text("synthetic metadata\n", encoding="utf-8")

    def snapshot() -> dict[Path, tuple[bytes, int, int]]:
        return {
            path.relative_to(tmp_path): (
                path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns
            )
            for path in tmp_path.rglob("*") if path.is_file()
        }

    before_files = snapshot()
    records: list[tuple[MachineRecord, MachineRecord]] = []

    def build(root: str, os_name: str = "windows") -> WorkstationPathResolver:
        record = MachineRecord(
            key="synthetic", hostname="", hostname_aliases=(), os=os_name,
            workspace_root=root, ssh=None,
            raw={"workspace_root": root, "metadata": {"tags": ["preserve"]}},
        )
        records.append((record, deepcopy(record)))
        return WorkstationPathResolver({record.key: record})

    yield build

    assert snapshot() == before_files
    for record, before_record in records:
        assert record == before_record


@pytest.mark.parametrize("root_drive", ["R", "r"])
@pytest.mark.parametrize("input_drive", ["R", "r"])
@pytest.mark.parametrize("suffix", [
    "docs/guide.md", "bundles/drop.zip", "logs/run.log", "tools/helper.exe",
])
def test_native_and_git_bash_suffixes_agree(
    tmp_path: Path, resolver_factory: Callable[..., WorkstationPathResolver],
    root_drive: str, input_drive: str, suffix: str,
) -> None:
    # Hand calculation: R:\FixtureRoot\docs\guide.md and /r/FixtureRoot/docs/guide.md
    # both leave docs/guide.md. Apply that same prefix removal to each literal
    # suffix above; only the drive letter changes case, never the tail.
    root = root_drive + ":" + "\\FixtureRoot"
    resolver = resolver_factory(root)
    native = input_drive + ":" + "\\FixtureRoot\\" + suffix.replace("/", "\\")
    git_bash = "/" + input_drive + "/FixtureRoot/" + suffix
    caller = tmp_path / "checkout"

    assert resolver.rewrite_workspace_path(native, caller) == suffix
    assert resolver.rewrite_workspace_path(git_bash, caller) == suffix


@pytest.mark.parametrize("prefix", ["r:/Fixture Root/", "/R/Fixture Root/"])
def test_spaced_mixed_separator_suffix(
    tmp_path: Path, resolver_factory: Callable[..., WorkstationPathResolver], prefix: str,
) -> None:
    # Hand calculation: discard R:/Fixture Root/; bundle drop, Run Logs and the
    # filename remain, with spaces and case intact and backslashes made slashes.
    resolver = resolver_factory("R:" + "\\Fixture Root")
    original = prefix + "bundle drop\\Run Logs/daily log.txt"

    assert resolver.rewrite_workspace_path(original, tmp_path / "checkout") == (
        "bundle drop/Run Logs/daily log.txt"
    )


@pytest.mark.parametrize("original", [
    r"\\fixture\share\FixtureRoot\docs\guide.md",
    "//fixture/share/FixtureRoot/docs/guide.md",
])
def test_unc_like_prefix_suffix(
    tmp_path: Path, resolver_factory: Callable[..., WorkstationPathResolver], original: str,
) -> None:
    # Hand calculation: after slash normalization, removing the declared share
    # root and separator leaves docs/guide.md. No network share is accessed.
    resolver = resolver_factory(r"\\fixture\share\FixtureRoot")

    assert resolver.rewrite_workspace_path(original, tmp_path / "checkout") == "docs/guide.md"


@pytest.mark.parametrize("original", [
    "R:/FixtureRoot", "r:/FixtureRoot/", "/R/FixtureRoot", "/r/FixtureRoot/",
])
def test_workspace_root_becomes_dot(
    tmp_path: Path, resolver_factory: Callable[..., WorkstationPathResolver], original: str,
) -> None:
    # Hand calculation: removing the whole workspace root leaves an empty suffix;
    # the resolver's public relative-root representation is the literal dot.
    resolver = resolver_factory("R:" + "\\FixtureRoot")

    assert resolver.rewrite_workspace_path(original, tmp_path / "checkout") == "."


def test_posix_source_suffix(
    tmp_path: Path, resolver_factory: Callable[..., WorkstationPathResolver],
) -> None:
    # Hand calculation: the temporary source root followed by docs/guide.md
    # leaves docs/guide.md. This input also names an actual synthetic source file.
    root = tmp_path / "source"
    original = str(root / "docs" / "guide.md")
    resolver = resolver_factory(str(root), os_name="linux")

    assert resolver.rewrite_workspace_path(original, tmp_path / "checkout") == "docs/guide.md"


@pytest.mark.parametrize("original", [
    "R:/FixtureRoot-copy/docs/guide.md",
    r"S:\FixtureRoot\docs\guide.md",
    "/s/FixtureRoot/docs/guide.md",
    "//fixture/other/FixtureRoot/docs/guide.md",
])
def test_nonmatching_root_preserved(
    tmp_path: Path, resolver_factory: Callable[..., WorkstationPathResolver], original: str,
) -> None:
    # Hand calculation: a shared name fragment is not a complete root component;
    # a different drive or share is not registered. No prefix can be removed, so
    # every character of the input (including backslashes) must be retained.
    resolver = resolver_factory("R:" + "\\FixtureRoot")
    share_resolver = resolver_factory(r"\\fixture\share\FixtureRoot")

    assert resolver.rewrite_workspace_path(original, tmp_path / "checkout") == original
    assert share_resolver.rewrite_workspace_path(original, tmp_path / "checkout") == original
