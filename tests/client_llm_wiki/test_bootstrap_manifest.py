"""Atomic render-manifest publication and independent attestation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat

import pytest
from client_llm_wiki import bootstrap_manifest
from client_llm_wiki.bootstrap_manifest import (
    BootstrapManifestError,
    persist_render_manifest,
    validate_render_manifest,
)
from client_llm_wiki.bootstrap_renderer import bind_empty_clone


def _clone(tmp_path: Path, *, populated: bool = True) -> Path:
    clone = tmp_path / "clone"
    (clone / ".git").mkdir(parents=True)
    (clone / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")
    if not populated:
        return clone
    _populate(clone)
    return clone


def _populate(clone: Path) -> None:
    (clone / ".gitignore").write_text("private-output/\n")
    (clone / ".gitignore").chmod(0o644)
    (clone / ".claude").mkdir()
    (clone / ".claude" / "CLAUDE.md").write_text("private\n")
    (clone / ".claude" / "CLAUDE.md").chmod(0o644)
    (clone / "README.md").write_text("hello\n")
    (clone / "README.md").chmod(0o644)
    (clone / "run.sh").write_text("#!/bin/sh\n")
    (clone / "run.sh").chmod(0o755)


def _publish(tmp_path: Path):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence" / "render.json"
    destination.parent.mkdir()
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        result = persist_render_manifest(
            bound, destination, registered_repo="org/llm-wiki-client",
            allowed_origins=("https://github.com/org/llm-wiki-client.git",),
            template_commit="a" * 40, template_tree="b" * 40,
        )
    return clone, destination, result


def test_manifest_covers_identities_members_and_firewall(tmp_path):
    clone, destination, result = _publish(tmp_path)
    payload = json.loads(destination.read_text())

    assert payload["version"] == 1
    assert payload["registered_repo"] == "org/llm-wiki-client"
    assert payload["template"] == {"commit": "a" * 40, "tree": "b" * 40}
    assert set(payload["identities"]) == {"parent", "root", "git", "config", "manifest_parent"}
    assert payload["members"]["README.md"]["sha256"]
    assert payload["members"]["run.sh"]["mode"] == 0o755
    assert payload["members"][".claude"]["type"] == "directory"
    assert payload["memberships"][""] == sorted([".git", ".gitignore", ".claude", "README.md", "run.sh"])
    assert payload["firewall"] == [".claude/CLAUDE.md", ".gitignore"]
    assert result.bytes == destination.read_bytes()
    validate_render_manifest(clone, destination, result)


@pytest.mark.parametrize("mutation", ["same_bytes", "size", "mode", "firewall", "member"])
def test_independent_validation_rejects_render_substitution(tmp_path, mutation):
    clone, destination, result = _publish(tmp_path)
    readme = clone / "README.md"
    if mutation == "same_bytes":
        readme.write_bytes(b"jello\n")
    elif mutation == "size":
        readme.write_bytes(b"longer\n")
    elif mutation == "mode":
        readme.chmod(0o755)
    elif mutation == "firewall":
        (clone / ".gitignore").write_bytes(b"public-output/\n")
    else:
        (clone / "surprise").write_bytes(b"x")

    with pytest.raises(BootstrapManifestError):
        validate_render_manifest(clone, destination, result)


@pytest.mark.parametrize("mutation", ["target", "config", "manifest_parent", "final"])
def test_independent_validation_rejects_identity_substitution(tmp_path, mutation):
    clone, destination, result = _publish(tmp_path)
    if mutation == "target":
        clone.rename(tmp_path / "old-clone")
        _clone(tmp_path)
    elif mutation == "config":
        config = clone / ".git/config"
        config.rename(clone / ".git/config.old")
        config.write_bytes(b"[core]\n")
    elif mutation == "manifest_parent":
        destination.parent.rename(tmp_path / "old-evidence")
        destination.parent.mkdir()
        destination.write_bytes(result.bytes)
        destination.chmod(0o600)
    else:
        destination.rename(destination.with_suffix(".old"))
        destination.write_bytes(result.bytes)
        destination.chmod(0o600)

    with pytest.raises(BootstrapManifestError):
        validate_render_manifest(clone, destination, result)


@pytest.mark.parametrize("kind", ["inside", "symlink", "directory", "wrong_mode"])
def test_manifest_destination_rejects_unsafe_entry(tmp_path, kind):
    clone = _clone(tmp_path, populated=False)
    parent = clone if kind == "inside" else tmp_path / "evidence"
    parent.mkdir(exist_ok=True)
    destination = parent / "render.json"
    if kind == "symlink":
        destination.symlink_to(tmp_path / "elsewhere")
    elif kind == "directory":
        destination.mkdir()
    elif kind == "wrong_mode":
        destination.write_bytes(b"partial")
        destination.chmod(0o644)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            persist_render_manifest(
                bound, destination, registered_repo="org/repo",
                allowed_origins=("https://github.com/org/repo",),
                template_commit="a" * 40, template_tree="b" * 40,
            )


def test_partial_or_non_0600_manifest_is_rejected(tmp_path):
    clone, destination, result = _publish(tmp_path)
    destination.write_bytes(result.bytes[:20])
    with pytest.raises(BootstrapManifestError):
        validate_render_manifest(clone, destination, result)
    destination.write_bytes(result.bytes)
    destination.chmod(0o644)
    with pytest.raises(BootstrapManifestError):
        validate_render_manifest(clone, destination, result)


def test_public_api_has_no_callback_or_failpoint(tmp_path):
    with pytest.raises(TypeError):
        persist_render_manifest(None, tmp_path / "x", callback=lambda: None)
    with pytest.raises(TypeError):
        persist_render_manifest(None, tmp_path / "x", failpoint="replace")


def test_publication_syncs_file_then_replaces_and_syncs_parent(tmp_path, monkeypatch):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    events: list[str] = []
    real_fdatasync, real_fsync, real_replace = os.fdatasync, os.fsync, os.replace
    monkeypatch.setattr(bootstrap_manifest.os, "fdatasync", lambda fd: (events.append("file-sync"), real_fdatasync(fd))[1])
    monkeypatch.setattr(bootstrap_manifest.os, "replace", lambda *a, **k: (events.append("replace"), real_replace(*a, **k))[1])
    monkeypatch.setattr(bootstrap_manifest.os, "fsync", lambda fd: (events.append("parent-sync"), real_fsync(fd))[1])
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        persist_render_manifest(
            bound, destination, registered_repo="org/repo",
            allowed_origins=("https://github.com/org/repo",),
            template_commit="a" * 40, template_tree="b" * 40,
        )
    assert events == ["file-sync", "replace", "parent-sync"]
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600


@pytest.mark.parametrize("stage", ["temp_synced", "published"])
def test_attests_after_each_internal_operation(tmp_path, monkeypatch, stage):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()

    def substitute(current):
        if current == stage:
            (clone / "README.md").write_bytes(b"jello\n")

    monkeypatch.setattr(bootstrap_manifest, "_after_operation", substitute)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            persist_render_manifest(
                bound, destination, registered_repo="org/repo",
                allowed_origins=("https://github.com/org/repo",),
                template_commit="a" * 40, template_tree="b" * 40,
            )
