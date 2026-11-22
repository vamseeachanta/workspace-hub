"""Offline recovery tests; all input bytes and paths are synthetic fixtures."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

# Two parents above tests/memory is the repository root (repository layout).
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/memory/local_memory_backup.py"
ORIGINAL = {
    "MEMORY.md": b"# Synthetic memory\r\nkeep exact endings\r\n",
    "topics/spaced filename.md": b"first\nsecond\x00\xff\n",
    "empty.bin": b"",
    "manifest.json": b"source file, not snapshot metadata\n",
    "topics/caf\u00e9.md": "synthetic text: \u03bb\n".encode("utf-8"),
}


@pytest.fixture(scope="module")
def backup():
    spec = importlib.util.spec_from_file_location("local_memory_backup", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    for name, content in ORIGINAL.items():
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
    return root


def contents(root):
    return {
        file.relative_to(root).as_posix(): file.read_bytes()
        for file in root.rglob("*") if file.is_file()
    }


def manifest(snapshot):
    return json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))


def save_manifest(snapshot, data):
    (snapshot / "manifest.json").write_text(json.dumps(data), encoding="utf-8")


def test_snapshot_restore_exact_bytes(backup, source, tmp_path):
    snap = tmp_path / "snapshots" / "first copy"
    backup.snapshot(source, snap)
    assert manifest(snap) == {
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in ORIGINAL.items()}
    }
    assert contents(snap / "files") == ORIGINAL
    assert contents(source) == ORIGINAL
    # Simulate damaged live input, then recover from the independent copy.
    (source / "MEMORY.md").write_bytes(b"damaged live input")
    before = contents(snap)
    target = tmp_path / "restored"
    backup.restore(snap, target)
    assert contents(target) == ORIGINAL
    assert contents(snap) == before
    assert (source / "MEMORY.md").read_bytes() == b"damaged live input"


@pytest.mark.parametrize("existing_empty", [False, True])
def test_corrupt_snapshot_refused(backup, source, tmp_path, existing_empty):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    # Sorts after MEMORY.md: no earlier valid entry may be written either.
    (snap / "files/topics/spaced filename.md").write_bytes(b"corrupt")
    target = tmp_path / "restored"
    if existing_empty:
        target.mkdir()
    with pytest.raises(ValueError, match="digest"):
        backup.restore(snap, target)
    assert list(target.iterdir()) == [] if existing_empty else not target.exists()


def test_nonempty_restore_target_refused(backup, source, tmp_path):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    target = tmp_path / "restored"
    target.mkdir()
    (target / ".keep").write_bytes(b"do not overwrite")
    with pytest.raises((ValueError, FileExistsError)):
        backup.restore(snap, target)
    assert contents(target) == {".keep": b"do not overwrite"}
    assert contents(source) == ORIGINAL


def test_restore_to_existing_empty_target(backup, source, tmp_path):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    target = tmp_path / "restored"
    target.mkdir()
    backup.restore(snap, target)
    assert contents(target) == ORIGINAL


def test_existing_snapshot_refused(backup, source, tmp_path):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    before = contents(snap)
    with pytest.raises((ValueError, FileExistsError)):
        backup.snapshot(source, snap)
    assert contents(snap) == before
    empty = tmp_path / "existing empty snapshot"
    empty.mkdir()
    with pytest.raises((ValueError, FileExistsError)):
        backup.snapshot(source, empty)
    assert list(empty.iterdir()) == []


@pytest.mark.parametrize("missing", ["manifest.json", "files/MEMORY.md", "files"])
def test_missing_snapshot_entry_refused(backup, source, tmp_path, missing):
    # Construct incomplete input without deleting any fixture data.
    snap = tmp_path / "snapshot"
    snap.mkdir()
    if missing != "files":
        (snap / "files").mkdir()
    if missing != "manifest.json":
        save_manifest(snap, {"files": {"MEMORY.md": hashlib.sha256(ORIGINAL["MEMORY.md"]).hexdigest()}})
    target = tmp_path / "restored"
    with pytest.raises((ValueError, FileNotFoundError)):
        backup.restore(snap, target)
    assert not target.exists()


@pytest.mark.parametrize("name", ["../escape", "/escape", "a/../../escape", "a//b", "./a", "a/", "a\\b", "", "a\x00b"])
def test_manifest_path_escape_refused(backup, source, tmp_path, name):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    data = manifest(snap)
    data["files"][name] = hashlib.sha256(b"escape").hexdigest()
    save_manifest(snap, data)
    target = tmp_path / "restored"
    with pytest.raises(ValueError):
        backup.restore(snap, target)
    assert not target.exists()


@pytest.mark.parametrize("data", [[], {}, {"files": []}, {"files": {"a": "bad digest"}}, {"files": {"a": None}}, {"files": {}, "extra": True}])
def test_invalid_manifest_refused(backup, source, tmp_path, data):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    save_manifest(snap, data)
    target = tmp_path / "restored"
    with pytest.raises(ValueError):
        backup.restore(snap, target)
    assert not target.exists()


@pytest.mark.parametrize("text", ['{"files": {}, "files": {}}', '{"files": {"a": "x", "a": "y"}}', "not json"])
def test_duplicate_or_malformed_manifest_refused(backup, source, tmp_path, text):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    (snap / "manifest.json").write_text(text, encoding="utf-8")
    target = tmp_path / "restored"
    with pytest.raises(ValueError):
        backup.restore(snap, target)
    assert not target.exists()


@pytest.mark.parametrize("location", ["files/unlisted", "unlisted"])
def test_unlisted_snapshot_entry_refused(backup, source, tmp_path, location):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    (snap / location).write_bytes(b"unlisted")
    target = tmp_path / "restored"
    with pytest.raises(ValueError):
        backup.restore(snap, target)
    assert not target.exists()


@pytest.mark.parametrize("location", ["file", "directory", "root", "ancestor"])
def test_source_symlink_refused(backup, source, tmp_path, location):
    candidate = source
    if location == "file":
        (source / "link").symlink_to(source / "MEMORY.md")
    elif location == "directory":
        (source / "link").symlink_to(source / "topics", target_is_directory=True)
    elif location == "root":
        candidate = tmp_path / "link"
        candidate.symlink_to(source, target_is_directory=True)
    else:
        link = tmp_path / "link"
        link.symlink_to(tmp_path, target_is_directory=True)
        candidate = link / "source"
    snap = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="symlink"):
        backup.snapshot(candidate, snap)
    assert not snap.exists()
    assert (source / "MEMORY.md").read_bytes() == ORIGINAL["MEMORY.md"]


@pytest.mark.parametrize("location", ["extra", "manifest", "payload", "root", "ancestor"])
def test_snapshot_symlink_refused(backup, source, tmp_path, location):
    snap = tmp_path / "snapshot"
    if location in {"manifest", "payload"}:
        snap.mkdir()
        (snap / "files").mkdir()
        if location == "manifest":
            (snap / "manifest.json").symlink_to(source / "manifest.json")
        else:
            (snap / "files/MEMORY.md").symlink_to(source / "MEMORY.md")
            save_manifest(snap, {"files": {"MEMORY.md": hashlib.sha256(ORIGINAL["MEMORY.md"]).hexdigest()}})
    else:
        backup.snapshot(source, snap)
        if location == "extra":
            (snap / "files/link").symlink_to(source / "MEMORY.md")
        else:
            link = tmp_path / "link"
            link.symlink_to(snap if location == "root" else tmp_path, target_is_directory=True)
            snap = link if location == "root" else link / "snapshot"
    target = tmp_path / "restored"
    with pytest.raises(ValueError, match="symlink"):
        backup.restore(snap, target)
    assert not target.exists()


@pytest.mark.parametrize("operation", ["snapshot", "restore"])
@pytest.mark.parametrize("location", ["root", "ancestor", "dangling"])
def test_destination_symlink_refused(backup, source, tmp_path, operation, location):
    snap = tmp_path / "snapshot"
    if operation == "restore":
        backup.snapshot(source, snap)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "link"
    link.symlink_to(tmp_path / "absent" if location == "dangling" else outside, target_is_directory=True)
    destination = link / "new" if location == "ancestor" else link
    with pytest.raises(ValueError, match="symlink"):
        if operation == "snapshot":
            backup.snapshot(source, destination)
        else:
            backup.restore(snap, destination)
    assert list(outside.iterdir()) == []
    assert not (tmp_path / "absent").exists()


def test_special_source_refused(backup, source, tmp_path):
    os.mkfifo(source / "pipe")
    snap = tmp_path / "snapshot"
    with pytest.raises(ValueError):
        backup.snapshot(source, snap)
    assert not snap.exists()


def test_overlapping_paths_refused(backup, source, tmp_path):
    with pytest.raises(ValueError):
        backup.snapshot(source, source / "snapshot")
    assert not (source / "snapshot").exists()
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    with pytest.raises(ValueError):
        backup.restore(snap, snap / "restored")
    assert not (snap / "restored").exists()
    assert contents(source) == ORIGINAL


def test_list_snapshots(backup, source, tmp_path):
    root = tmp_path / "snapshots"
    root.mkdir()
    assert backup.list_snapshots(root) == []
    backup.snapshot(source, root / "second")
    backup.snapshot(source, root / "first copy")
    before = contents(root)
    assert backup.list_snapshots(root) == ["first copy", "second"]
    assert contents(root) == before
    (root / "second/files/MEMORY.md").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="digest"):
        backup.list_snapshots(root)


def test_empty_source(backup, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    target = tmp_path / "restored"
    backup.restore(snap, target)
    assert target.is_dir()
    assert list(target.iterdir()) == []


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, check=False)


def test_cli_explicit_paths(source, tmp_path):
    root = tmp_path / "snapshots"
    snap = root / "first copy"
    target = tmp_path / "restored"
    for args in [("snapshot", "--source", source, "--snapshot", snap),
                 ("restore", "--snapshot", snap, "--target", target)]:
        result = run_cli(*args)
        # Zero is the documented successful process exit status.
        assert result.returncode == 0, result.stderr
    result = run_cli("list", "--snapshots-dir", root)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == ["first copy"]
    assert contents(target) == ORIGINAL
    assert contents(source) == ORIGINAL
    result = run_cli("restore", "--snapshot", snap, "--target", target)
    assert result.returncode != 0
    assert contents(target) == ORIGINAL


@pytest.mark.parametrize("command", ["snapshot", "restore", "list"])
def test_cli_requires_explicit_paths(tmp_path, command):
    result = run_cli(command)
    assert result.returncode != 0
    assert "required" in result.stderr


@pytest.mark.parametrize("kind", ["missing", "file"])
def test_invalid_source_writes_nothing(backup, tmp_path, kind):
    source = tmp_path / "source"
    if kind == "file":
        source.write_bytes(b"not a directory")
    snap = tmp_path / "new parent/snapshot"
    with pytest.raises(ValueError):
        backup.snapshot(source, snap)
    assert not snap.parent.exists()


def test_special_snapshot_entry_refused(backup, source, tmp_path):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    os.mkfifo(snap / "files/pipe")
    target = tmp_path / "new parent/restored"
    with pytest.raises(ValueError):
        backup.restore(snap, target)
    assert not target.parent.exists()


def test_payload_directory_symlink_refused(backup, source, tmp_path):
    snap = tmp_path / "snapshot"
    snap.mkdir()
    save_manifest(snap, {"files": {}})
    (snap / "files").symlink_to(source, target_is_directory=True)
    target = tmp_path / "restored"
    with pytest.raises(ValueError, match="symlink"):
        backup.restore(snap, target)
    assert not target.exists()


def test_symlink_before_parent_traversal_refused(backup, source, tmp_path):
    (tmp_path / "link").symlink_to(source / "topics", target_is_directory=True)
    snap = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="symlink"):
        backup.snapshot(tmp_path / "link" / "..", snap)
    assert not snap.exists()


def test_list_symlink_refused(backup, source, tmp_path):
    root = tmp_path / "snapshots"
    backup.snapshot(source, root / "valid")
    (root / "link").symlink_to(root / "valid", target_is_directory=True)
    before = contents(root / "valid")
    with pytest.raises(ValueError, match="symlink"):
        backup.list_snapshots(root)
    assert contents(root / "valid") == before


def test_restore_file_target_refused(backup, source, tmp_path):
    snap = tmp_path / "snapshot"
    backup.snapshot(source, snap)
    target = tmp_path / "restored"
    target.write_bytes(b"existing file")
    with pytest.raises(ValueError):
        backup.restore(snap, target)
    assert target.read_bytes() == b"existing file"
