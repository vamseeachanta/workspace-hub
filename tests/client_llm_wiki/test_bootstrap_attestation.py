"""Descriptor race controls for render-manifest attestation."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import pytest
from client_llm_wiki import bootstrap_attestation, bootstrap_manifest
from client_llm_wiki.bootstrap_manifest import BootstrapManifestError, persist_render_manifest
from client_llm_wiki.bootstrap_renderer import bind_empty_clone
REPO = "org/llm-wiki-client"
ORIGINS = (
    "git@github.com:org/llm-wiki-client.git",
    "https://github.com/org/llm-wiki-client.git",
)
def _clone(tmp_path: Path) -> Path:
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", str(clone)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clone), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
    subprocess.run(["git", "-C", str(clone), "remote", "add", "origin", ORIGINS[1]], check=True)
    return clone
def _populate(clone: Path) -> None:
    (clone / ".gitignore").write_text("private-output/\n")
    (clone / ".gitignore").chmod(0o644)
    (clone / ".claude").mkdir()
    (clone / ".claude/CLAUDE.md").write_text("private\n")
    (clone / ".claude/CLAUDE.md").chmod(0o644)
    (clone / "README.md").write_text("hello\n")
    (clone / "README.md").chmod(0o644)
    (clone / "run.sh").write_text("#!/bin/sh\n")
    (clone / "run.sh").chmod(0o755)
def _persist(bound, destination: Path):
    return persist_render_manifest(
        bound, destination, registered_repo=REPO, allowed_origins=ORIGINS,
        template_commit="a" * 40, template_tree="b" * 40,
    )
@pytest.mark.parametrize("relative", ["README.md", ".claude"])
def test_same_name_member_replacement_race_is_rejected(tmp_path, monkeypatch, relative):
    clone, destination = _clone(tmp_path), tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    def replace_entry(path, is_directory):
        if path != relative:
            return
        entry = clone / path
        entry.rename(entry.with_name(entry.name + ".old"))
        if is_directory:
            entry.mkdir()
            (entry / "CLAUDE.md").write_text("private\n")
            (entry / "CLAUDE.md").chmod(0o644)
        else:
            entry.write_text("hello\n")
            entry.chmod(0o644)
    monkeypatch.setattr(bootstrap_attestation, "after_member_scan", replace_entry)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError, match="parent entry"):
            _persist(bound, destination)
@pytest.mark.parametrize("read_index", [0, 1])
def test_in_place_manifest_mutation_between_link_reads_is_rejected(
    tmp_path, monkeypatch, read_index,
):
    clone, destination = _clone(tmp_path), tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    def mutate(index):
        if index == read_index:
            data = destination.read_bytes()
            destination.write_bytes(data[:-2] + b" " + data[-1:])
    monkeypatch.setattr(bootstrap_manifest, "_after_link_read", mutate)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            _persist(bound, destination)
def test_in_place_manifest_mutation_inside_held_read_is_rejected(tmp_path, monkeypatch):
    clone, destination = _clone(tmp_path), tmp_path / "evidence/render.json"
    destination.parent.mkdir()
    real_read, mutated = os.read, False
    def race(descriptor, size):
        nonlocal mutated
        data = real_read(descriptor, size)
        if data and destination.exists() and not mutated:
            if os.fstat(descriptor).st_ino == destination.stat().st_ino:
                mutated = True
                current = destination.read_bytes()
                destination.write_bytes(current[:-2] + b" " + current[-1:])
        return data
    monkeypatch.setattr(bootstrap_attestation.os, "read", race)
    with bind_empty_clone(clone) as bound:
        _populate(clone)
        with pytest.raises(BootstrapManifestError):
            _persist(bound, destination)
