#!/usr/bin/env python3
"""Explicit, offline snapshots of regular files, with byte-exact recovery.

CLI (all paths are required; no memory directory is selected implicitly)::

    python scripts/memory/local_memory_backup.py snapshot --source SOURCE --snapshot SNAPSHOT
    python scripts/memory/local_memory_backup.py list --snapshots-dir DIRECTORY
    python scripts/memory/local_memory_backup.py restore --snapshot SNAPSHOT --target TARGET

A new SNAPSHOT contains manifest.json (a JSON object with a single "files" map
from relative POSIX filenames to lowercase SHA-256 digests) and a files/ tree.
SHA-256 is the algorithm named in FIPS 180-4, Secure Hash Standard. Source files
named manifest.json are ordinary payloads beneath files/. Listing validates each
snapshot in DIRECTORY and prints its sorted names as a JSON array; invalid entries
are errors. Restore validates the entire snapshot before creating output, then
writes only into an absent or empty TARGET. Existing snapshots are always refused.
Symlinks (including path ancestors), special files, unsafe manifest paths and
unlisted payload files are refused. No source is changed and nothing is deleted.

Only file names and bytes are preserved: empty directories, permissions, ownership
and timestamps are not recovery metadata. All payload bytes are held in memory.
Use quiescent directories under trusted local control: this is not a transaction
against concurrent filesystem writers. I/O failures during writing can leave a
partial destination for inspection; it is never automatically removed or replaced.
Digests detect accidental damage, not malicious replacement of payload and manifest.
No bridge, scheduler, network, retention or deletion operation is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys


def _path(value: Path | str) -> Path:
    """Reject symlinks before normalizing, including a symlink followed by '..'."""
    path = Path(value).absolute()
    for part in reversed((path, *path.parents)):
        if part.is_symlink():
            raise ValueError("symlink paths are forbidden")
    return Path(os.path.abspath(path))


def _disjoint(left: Path, right: Path) -> None:
    if left == right or left in right.parents or right in left.parents:
        raise ValueError("source and destination paths must not overlap")


def _relative_name(name: str) -> None:
    if (not name or "\x00" in name or "\\" in name
            or PurePosixPath(name).is_absolute() or PureWindowsPath(name).drive
            or any(part in {"", ".", ".."} for part in name.split("/"))):
        raise ValueError("unsafe relative filename")


def _read_file(path: Path) -> bytes:
    path = _path(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("only regular files are supported")
    # O_NOFOLLOW prevents a last-component symlink swap; O_NONBLOCK avoids
    # waiting on a FIFO substituted between the metadata check and open.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("only regular files are supported")
        return stream.read()


def _read_tree(root: Path) -> dict[str, bytes]:
    root = _path(root)
    if not root.is_dir():
        raise ValueError("a directory is required")
    files = {}
    pending = [root]
    while pending:
        directory = _path(pending.pop())
        for entry in sorted(directory.iterdir()):
            entry = _path(entry)
            name = entry.relative_to(root).as_posix()
            _relative_name(name)
            mode = entry.lstat().st_mode
            if stat.S_ISDIR(mode):
                pending.append(entry)
            elif stat.S_ISREG(mode):
                files[name] = _read_file(entry)
            else:
                raise ValueError("only directories and regular files are supported")
    return files


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate manifest key")
        result[key] = value
    return result


def _validated_snapshot(snapshot_path: Path) -> dict[str, bytes]:
    root = _path(snapshot_path)
    if not root.is_dir():
        raise ValueError("snapshot directory is required")
    for entry in root.iterdir():
        _path(entry)
    if {entry.name for entry in root.iterdir()} != {"manifest.json", "files"}:
        raise ValueError("snapshot entries are missing or unlisted")
    manifest = json.loads(_read_file(root / "manifest.json"), object_pairs_hook=_unique_object)
    if (not isinstance(manifest, dict) or set(manifest) != {"files"}
            or not isinstance(manifest["files"], dict)):
        raise ValueError("invalid manifest structure")
    expected = manifest["files"]
    for name, digest in expected.items():
        _relative_name(name)
        # Each byte is encoded by two hexadecimal digits (base-16 encoding).
        if (not isinstance(digest, str)
                or len(digest) != hashlib.sha256().digest_size * 2
                or re.fullmatch(r"[0-9a-f]+", digest) is None):
            raise ValueError("invalid SHA-256 digest")
    files = _read_tree(root / "files")
    if files.keys() != expected.keys():
        raise ValueError("payload entries are missing or unlisted")
    for name, content in files.items():
        if hashlib.sha256(content).hexdigest() != expected[name]:
            raise ValueError("snapshot digest mismatch")
    return files


def _write_files(root: Path, files: dict[str, bytes]) -> None:
    for name, content in sorted(files.items()):
        target = _path(root / name)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)


def snapshot(source: Path | str, destination: Path | str) -> None:
    """Create a new snapshot; an existing destination, even empty, is refused."""
    source, destination = _path(source), _path(destination)
    _disjoint(source, destination)
    if destination.exists():
        raise FileExistsError("snapshot destination already exists")
    files = _read_tree(source)
    destination.mkdir(parents=True, exist_ok=False)
    payload = destination / "files"
    payload.mkdir()
    _write_files(payload, files)
    manifest = {"files": {name: hashlib.sha256(data).hexdigest()
                          for name, data in sorted(files.items())}}
    # Write the manifest last; interrupted snapshots fail integrity validation.
    with (destination / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=True, sort_keys=True)
        stream.write("\n")


def list_snapshots(directory: Path | str) -> list[str]:
    """Return sorted snapshot names only after every entry passes validation."""
    root = _path(directory)
    if not root.is_dir():
        raise ValueError("snapshot collection directory is required")
    names = []
    for entry in sorted(root.iterdir()):
        _validated_snapshot(entry)
        names.append(entry.name)
    return names


def restore(snapshot_path: Path | str, target: Path | str) -> None:
    """Validate all bytes before writing into an absent or empty target."""
    snapshot_path, target = _path(snapshot_path), _path(target)
    _disjoint(snapshot_path, target)
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError("restore target must be an empty directory")
    files = _validated_snapshot(snapshot_path)
    if target.exists():
        if not target.is_dir() or any(target.iterdir()):
            raise ValueError("restore target must be an empty directory")
    else:
        target.mkdir(parents=True, exist_ok=False)
    _write_files(target, files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("snapshot")
    create.add_argument("--source", required=True, type=Path)
    create.add_argument("--snapshot", required=True, type=Path)
    listing = commands.add_parser("list")
    listing.add_argument("--snapshots-dir", required=True, type=Path)
    recovery = commands.add_parser("restore")
    recovery.add_argument("--snapshot", required=True, type=Path)
    recovery.add_argument("--target", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            snapshot(args.source, args.snapshot)
        elif args.command == "list":
            print(json.dumps(list_snapshots(args.snapshots_dir)))
        else:
            restore(args.snapshot, args.target)
    except (OSError, ValueError):
        # Do not echo payload bytes or private input paths into logs.
        print("Local backup refused: invalid input or filesystem operation failed.", file=sys.stderr)
        return 1  # Nonzero process status indicates failure (process exit convention).
    return 0  # Zero process status indicates success (process exit convention).


if __name__ == "__main__":
    raise SystemExit(main())
