"""Atomic render-manifest publication and independent attestation."""

from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import stat
import subprocess

import pytest
from client_llm_wiki import bootstrap_manifest
from client_llm_wiki.bootstrap_manifest import (
    BootstrapManifestError,
    persist_render_manifest,
    validate_render_manifest,
)
from client_llm_wiki.bootstrap_renderer import bind_empty_clone


REPO = "org/llm-wiki-client"
ORIGINS = (
    "git@github.com:org/llm-wiki-client.git",
    "https://github.com/org/llm-wiki-client.git",
)


def _clone(tmp_path: Path, *, populated: bool = True) -> Path:
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", str(clone)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clone), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
    subprocess.run(["git", "-C", str(clone), "remote", "add", "origin", ORIGINS[1]], check=True)
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
            bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
            template_commit="a" * 40, template_tree="b" * 40,
        )
    return clone, destination, result


def test_manifest_covers_identities_members_and_firewall(tmp_path):
    clone, destination, result = _publish(tmp_path)
    payload = json.loads(destination.read_text())

    assert payload["version"] == 1
    assert payload["registered_repo"] == REPO
    assert payload["template"] == {"commit": "a" * 40, "tree": "b" * 40}
    assert set(payload["identities"]) == {"parent", "root", "git", "config", "manifest_parent"}
    assert payload["members"]["README.md"]["sha256"]
    assert payload["members"]["run.sh"]["mode"] == 0o755
    assert payload["members"][".claude"]["type"] == "directory"
    assert payload["memberships"][""] == sorted([".git", ".gitignore", ".claude", "README.md", "run.sh"])
    assert payload["firewall"] == [".claude/CLAUDE.md", ".gitignore"]
    assert result.bytes == destination.read_bytes()
    backing = destination.parent / result.backing_name
    assert backing.stat().st_ino == destination.stat().st_ino
    assert destination.stat().st_nlink == 2
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


@pytest.mark.parametrize("kind", ["inside", "symlink", "directory", "wrong_mode", "placeholder"])
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
    elif kind == "placeholder":
        destination.write_bytes(b"partial")
        destination.chmod(0o600)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            persist_render_manifest(
                bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
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


def test_publication_syncs_file_then_links_and_syncs_parent(tmp_path, monkeypatch):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    events: list[str] = []
    real_fdatasync, real_fsync, real_link = os.fdatasync, os.fsync, os.link
    monkeypatch.setattr(bootstrap_manifest.os, "fdatasync", lambda fd: (events.append("file-sync"), real_fdatasync(fd))[1])
    monkeypatch.setattr(bootstrap_manifest.os, "link", lambda *a, **k: (events.append("link"), real_link(*a, **k))[1])
    monkeypatch.setattr(bootstrap_manifest.os, "fsync", lambda fd: (events.append("parent-sync"), real_fsync(fd))[1])
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        persist_render_manifest(
            bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
            template_commit="a" * 40, template_tree="b" * 40,
        )
    assert events == ["file-sync", "link", "parent-sync"]
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600


@pytest.mark.parametrize("stage", ["backing_synced", "published"])
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
        with pytest.raises(BootstrapManifestError) as raised:
            persist_render_manifest(
                bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
                template_commit="a" * 40, template_tree="b" * 40,
            )
    assert raised.value.backing_name
    assert (destination.parent / raised.value.backing_name).exists()


def test_concurrent_final_creation_is_not_overwritten(tmp_path, monkeypatch):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    real_link = os.link

    def race(*args, **kwargs):
        destination.write_bytes(b"victim")
        return real_link(*args, **kwargs)

    monkeypatch.setattr(bootstrap_manifest.os, "link", race)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError) as raised:
            persist_render_manifest(
                bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
                template_commit="a" * 40, template_tree="b" * 40,
            )
    assert destination.read_bytes() == b"victim"
    assert raised.value.backing_name
    assert (destination.parent / raised.value.backing_name).exists()


def test_in_place_config_edit_is_detected(tmp_path):
    clone, destination, result = _publish(tmp_path)
    config = clone / ".git/config"
    before = config.stat().st_ino
    config.write_bytes(config.read_bytes().replace(b"github.com", b"evil.example"))
    assert config.stat().st_ino == before
    with pytest.raises(BootstrapManifestError):
        validate_render_manifest(clone, destination, result)


def test_registered_origins_are_independently_validated(tmp_path):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            persist_render_manifest(
                bound, destination, registered_repo=REPO,
                allowed_origins=("https://example.invalid/repo",),
                template_commit="a" * 40, template_tree="b" * 40,
            )


def test_all_manifest_metadata_is_validated(tmp_path):
    clone, destination, result = _publish(tmp_path)
    metadata = dict(result.metadata)
    metadata["template"] = {"commit": "c" * 40, "tree": "d" * 40}
    with pytest.raises(BootstrapManifestError):
        validate_render_manifest(clone, destination, replace(result, metadata=metadata))


def test_directory_membership_must_be_stable_during_recursion(tmp_path, monkeypatch):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        real_scandir = os.scandir
        root_scans = 0

        def race(path):
            nonlocal root_scans
            if path == bound.root_fd:
                root_scans += 1
                if root_scans == 2:
                    (clone / "surprise").write_bytes(b"x")
            return real_scandir(path)

        monkeypatch.setattr(bootstrap_manifest.os, "scandir", race)
        with pytest.raises(BootstrapManifestError, match="membership changed"):
            persist_render_manifest(
                bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
                template_commit="a" * 40, template_tree="b" * 40,
            )


def test_enumeration_is_streamed_and_bounded(tmp_path, monkeypatch):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    monkeypatch.setattr(bootstrap_manifest, "_MAX_MEMBERS", 2)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        monkeypatch.setattr(bootstrap_manifest.os, "listdir", lambda *_a: pytest.fail("unbounded listdir"))
        with pytest.raises(BootstrapManifestError, match="member limit"):
            persist_render_manifest(
                bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
                template_commit="a" * 40, template_tree="b" * 40,
            )


def test_final_boundary_is_immediately_reattested(tmp_path, monkeypatch):
    clone = _clone(tmp_path, populated=False)
    destination = tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    monkeypatch.setattr(
        bootstrap_manifest, "_before_return",
        lambda: (clone / "README.md").write_bytes(b"jello\n"),
    )
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            persist_render_manifest(
                bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
                template_commit="a" * 40, template_tree="b" * 40,
            )
