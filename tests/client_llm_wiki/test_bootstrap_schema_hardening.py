"""Filesystem and linked-worktree hardening tests for issue #3449."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from client_llm_wiki import bootstrap_schema
from client_llm_wiki.bootstrap_schema import (
    RegistryValidationError,
    load_registry,
    parse_registry,
    validate_root_disjointness,
)


def _entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "short_name": "example-co",
        "repo": "example-org/llm-wiki-example-co",
        "visibility": "PRIVATE",
        "posture": "client-private",
        "status": "planned",
        "raw_roots": [],
        "raw_source_status": "not-mounted",
        "ingestion_enabled": False,
    }
    entry.update(overrides)
    return entry


def _registry(entries: list[dict[str, object]] | None = None) -> str:
    return yaml.safe_dump(
        {
            "registry_version": "0.2",
            "wikis": entries if entries is not None else [_entry()],
        },
        sort_keys=False,
    )


def test_schema_parsing_never_touches_raw_root_filesystem(monkeypatch):
    class ForbiddenPath:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("schema touched the filesystem through Path")

    class ForbiddenOS:
        def __getattr__(self, _name):
            raise AssertionError("schema touched the filesystem through os")

    monkeypatch.setattr(bootstrap_schema, "Path", ForbiddenPath)
    monkeypatch.setattr(bootstrap_schema, "os", ForbiddenOS())
    registry = parse_registry(
        _registry(
            [_entry(raw_roots=["/authorized/source"], raw_source_status="mounted")]
        )
    )
    assert registry.entries[0].raw_roots == ("/authorized/source",)


def _mounted_entry(root: str):
    return parse_registry(
        _registry([_entry(raw_roots=[root], raw_source_status="mounted")])
    ).entries[0]


@pytest.mark.parametrize(
    "protected",
    ["/workspace/private", "/workspace/private/raw", "/workspace/private/raw/cache"],
)
def test_lexical_overlap_is_rejected_in_both_directions(protected):
    entry = _mounted_entry("/workspace/private/raw")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            Path, "resolve", lambda *_args, **_kwargs: pytest.fail("resolved")
        )
        with pytest.raises(RegistryValidationError, match="overlaps"):
            validate_root_disjointness(entry, [protected])


def test_lexical_prefix_neighbor_is_not_an_overlap():
    validate_root_disjointness(
        _mounted_entry("/workspace/private/raw"), ["/workspace/privately"]
    )


@pytest.mark.parametrize("protected_kind", ["active", "canonical", "target"])
def test_validate_registry_rejects_each_linked_worktree_protected_root(
    tmp_path, monkeypatch, protected_kind
):
    active, canonical, _git_dir = _linked_module(tmp_path, monkeypatch)
    registry = tmp_path / "registry.yml"
    root = {
        "active": active,
        "canonical": canonical,
        "target": canonical.parent / "llm-wiki-example-co",
    }[protected_kind]
    registry.write_text(
        _registry([_entry(raw_roots=[str(root)], raw_source_status="mounted")]),
        encoding="utf-8",
    )
    with pytest.raises(RegistryValidationError, match="protected"):
        load_registry(registry)


def _linked_module(tmp_path: Path, monkeypatch):
    active = tmp_path / "active worktree"
    canonical = tmp_path / "canonical workspace " / "workspace-hub"
    git_dir = canonical / ".git" / "worktrees" / "active"
    module = active / "scripts" / "client_llm_wiki"
    module.mkdir(parents=True)
    git_dir.mkdir(parents=True)
    (active / ".git").write_text(f"gitdir: {git_dir}\n", encoding="utf-8")
    (git_dir / "commondir").write_text("../..\n", encoding="utf-8")
    monkeypatch.setattr(
        bootstrap_schema, "__file__", str(module / "bootstrap_schema.py")
    )
    return active, canonical, git_dir


def test_module_checkout_roots_preserves_valid_path_whitespace(tmp_path, monkeypatch):
    active, canonical, _git_dir = _linked_module(tmp_path, monkeypatch)
    assert bootstrap_schema._module_checkout_roots() == (active, canonical)


def test_module_checkout_roots_accepts_normal_checkout(tmp_path, monkeypatch):
    active = tmp_path / "normal checkout"
    module = active / "scripts" / "client_llm_wiki"
    module.mkdir(parents=True)
    (active / ".git").mkdir()
    monkeypatch.setattr(
        bootstrap_schema, "__file__", str(module / "bootstrap_schema.py")
    )
    assert bootstrap_schema._module_checkout_roots() == (active, active)


@pytest.mark.parametrize(
    "corruption",
    [
        "dot-git-symlink",
        "missing-gitdir",
        "gitdir-not-directory",
        "missing-common-directory",
        "common-not-directory",
        "commondir-symlink",
        "commondir-multiple-lines",
        "commondir-control",
        "forged-nonexistent-common",
    ],
)
def test_module_checkout_roots_rejects_untrusted_git_metadata(
    tmp_path, monkeypatch, corruption
):
    active, _canonical, git_dir = _linked_module(tmp_path, monkeypatch)
    dot_git = active / ".git"
    commondir = git_dir / "commondir"
    if corruption == "dot-git-symlink":
        dot_git.unlink()
        dot_git.symlink_to(git_dir)
    elif corruption == "missing-gitdir":
        dot_git.write_text(f"gitdir: {tmp_path / 'missing'}\n", encoding="utf-8")
    elif corruption == "gitdir-not-directory":
        fake = tmp_path / "gitdir-file"
        fake.write_text("not a directory", encoding="utf-8")
        dot_git.write_text(f"gitdir: {fake}\n", encoding="utf-8")
    elif corruption == "missing-common-directory":
        commondir.write_text("../../../missing/.git\n", encoding="utf-8")
    elif corruption == "common-not-directory":
        fake = tmp_path / "not-common.git"
        fake.write_text("not a directory", encoding="utf-8")
        commondir.write_text(str(fake) + "\n", encoding="utf-8")
    elif corruption == "commondir-symlink":
        commondir.unlink()
        target = tmp_path / "commondir-target"
        target.write_text("../..\n", encoding="utf-8")
        commondir.symlink_to(target)
    elif corruption == "commondir-multiple-lines":
        commondir.write_text("../..\n../../../other/.git\n", encoding="utf-8")
    elif corruption == "commondir-control":
        commondir.write_bytes(b"../\x00../.git\n")
    elif corruption == "forged-nonexistent-common":
        commondir.write_text("/nonexistent/.git\n", encoding="utf-8")
    with pytest.raises(RegistryValidationError, match="module Git"):
        bootstrap_schema._module_checkout_roots()
