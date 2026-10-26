#!/usr/bin/env python3
"""Inventory local output bundles and compare their byte-level manifests.

Usage::

    python scripts/reporting/bundle_manifest.py inventory BUNDLE
    python scripts/reporting/bundle_manifest.py inventory BUNDLE \
        --destination EXISTING_DIRECTORY --output manifest.json
    python scripts/reporting/bundle_manifest.py compare BEFORE.json AFTER.json

The local v1 protocol is {"schema": "bundle-manifest-v1", "files": [...]}; each
entry has exactly path, size (nonnegative integer bytes), and sha256 (lowercase
hexadecimal). Paths are relative POSIX paths. Entries and diff lists use Python
string lexical ordering, without case folding or Unicode normalization. UTF-8
JSON uses sorted keys, two-space indentation and a final newline. No timestamps,
source roots or environment metadata are emitted. JSON escaping preserves tabs,
newlines, quotes and other delimiters in filenames.

Inventory writes JSON to stdout unless --destination is supplied. --output is a
canonical relative POSIX path below that destination; its parent must exist.
No directories are created. The requested manifest alone is excluded from the
inventory, after checking its file type. Existing output must itself be a valid
bundle manifest: arbitrary payload files are never overwritten. No bundle data
is written; choosing a destination inside the bundle explicitly permits writing
only that manifest. Use an external destination or stdout for read-only storage.
Links (including hard-linked files), special files, linked directory ancestors,
non-UTF-8 filenames and escaping output paths are rejected. POSIX descriptor and
no-follow APIs are required. Input trees must be quiescent; this is not an atomic
snapshot, a concurrency guard, or a filesystem metadata comparison. Interrupted
manifest writes may be partial. SHA-256 compares bytes, not meaning, permissions,
empty directories, publication status, engineering validity or source rights;
renames appear as removal plus addition. Digest collisions remain possible.

Exit codes are local interface choices: inventory success and compare no-op are
0; compare with any added/removed/changed path is 1; invalid inputs, unsupported
versions, duplicate JSON keys/paths, non-finite numbers and filesystem errors are
2, with a generic diagnostic on stderr and no result on stdout. Compare validates
both manifests before emitting sorted added/removed/changed lists; unchanged
files are omitted. Input entry order is immaterial. There is no publication,
promotion, pruning, deletion or network operation.

SHA-256 basis: RFC 6234, sections 6.2 and 8.5:
https://www.rfc-editor.org/rfc/rfc6234.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


SCHEMA = "bundle-manifest-v1"  # First version of the local protocol above.
# RFC 6234 section 6.2: 256 bits / four bits per hexadecimal digit = 64 digits.
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
# Local I/O choice: 64 KiB bounds memory per file, independent of file size.
_READ_SIZE = 64 * 1024
# Local output permission choice: read/write bits, restricted by the caller's umask.
_OUTPUT_MODE = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
                | stat.S_IROTH | stat.S_IWOTH)


class ManifestError(ValueError):
    """The requested manifest or filesystem boundary is invalid."""


def _relative_path(value):
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ManifestError("invalid relative path")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ManifestError("invalid relative path") from exc
    path = PurePosixPath(value)
    if (path.is_absolute() or not path.parts or ".." in path.parts
            or path.as_posix() != value):
        raise ManifestError("invalid relative path")
    return value


def _validated(manifest):
    if (not isinstance(manifest, dict) or set(manifest) != {"schema", "files"}
            or manifest["schema"] != SCHEMA or not isinstance(manifest["files"], list)):
        raise ManifestError("invalid manifest schema")
    indexed = {}
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise ManifestError("invalid manifest entry")
        path = _relative_path(entry["path"])
        if path in indexed:
            raise ManifestError("duplicate manifest path")
        if type(entry["size"]) is not int or entry["size"] < 0:
            raise ManifestError("invalid byte size")
        if not isinstance(entry["sha256"], str) or not _DIGEST.fullmatch(entry["sha256"]):
            raise ManifestError("invalid SHA-256 digest")
        indexed[path] = entry
    for path in indexed:
        if any(parent.as_posix() in indexed for parent in PurePosixPath(path).parents):
            raise ManifestError("file path has a file ancestor")
    return indexed


def load_manifest(raw):
    """Read strict UTF-8 JSON and validate the entire v1 schema."""
    def unique_keys(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ManifestError("duplicate JSON key")
            result[key] = value
        return result

    def invalid_number(_value):
        raise ManifestError("non-finite JSON number")

    try:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        manifest = json.loads(text, object_pairs_hook=unique_keys, parse_constant=invalid_number)
        _validated(manifest)
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise ManifestError("manifest input is invalid") from exc
    return manifest


def serialize_manifest(manifest):
    """Return the canonical UTF-8 manifest bytes, independent of entry order."""
    entries = _validated(manifest)
    normalized = {"schema": SCHEMA, "files": [entries[path] for path in sorted(entries)]}
    return _json_bytes(normalized)


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def _directory(path):
    """Validate directory components without silently resolving any links."""
    path = Path(path)
    if ".." in path.parts:
        raise ManifestError("parent directory components are unsupported")
    path = path.absolute()
    current = Path(path.anchor)
    try:
        for part in path.parts[1:]:
            current /= part
            info = current.lstat()
            if not stat.S_ISDIR(info.st_mode) or _reparse_point(info):
                raise ManifestError("directory must not contain links or special files")
    except OSError as exc:
        raise ManifestError("directory input unavailable") from exc
    return path


def _reparse_point(info):
    # Windows junctions and other reparse points are links at the boundary.
    return bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _open_directory(path, *, dir_fd=None):
    return os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)


def _regular(info):
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ManifestError("only regular files without links are supported")


def read_manifest(path):
    """Read a regular manifest file without following links or opening a FIFO."""
    path = Path(path)
    parent = _directory(path.parent)
    parent_fd = _open_directory(parent)
    try:
        _regular(os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False))
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=parent_fd)
        with os.fdopen(descriptor, "rb") as source:
            _regular(os.fstat(source.fileno()))
            return load_manifest(source.read())
    finally:
        os.close(parent_fd)


def _file_digest(directory_fd, name):
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
    with os.fdopen(descriptor, "rb") as source:
        before = os.fstat(source.fileno())
        _regular(before)
        digest = hashlib.sha256()
        size = 0  # Empty stream has zero bytes; sum actual bytes below.
        while chunk := source.read(_READ_SIZE):
            digest.update(chunk)
            size += len(chunk)
        after = os.fstat(source.fileno())
        _regular(after)
        if (size != before.st_size or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns
                or before.st_ctime_ns != after.st_ctime_ns):
            raise ManifestError("file changed during inventory")
        return size, digest.hexdigest()


def inventory(root, *, exclude_output=None):
    """Read regular-file bytes without modifying payloads or following links."""
    root = _directory(root)
    excluded = Path(exclude_output).absolute() if exclude_output is not None else None
    entries = []

    # Each frame owns a directory descriptor and its remaining sorted names.
    # Retain ancestors for no-follow, descriptor-relative descent without using
    # Python call frames; siblings are opened only when visited.
    stack = []
    try:
        stack.append((_open_directory(root), "", None))
        while stack:
            directory_fd, prefix, names = stack[-1]
            if names is None:
                with os.scandir(directory_fd) as listing:
                    names = iter(sorted(entry.name for entry in listing))
                stack[-1] = (directory_fd, prefix, names)
            name = next(names, None)
            if name is None:
                stack.pop()
                os.close(directory_fd)
                continue
            relative = _relative_path(f"{prefix}/{name}" if prefix else name)
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if _reparse_point(info):
                raise ManifestError("directory must not contain links or special files")
            if stat.S_ISDIR(info.st_mode):
                stack.append((_open_directory(name, dir_fd=directory_fd), relative, None))
            else:
                _regular(info)  # Even an excluded output cannot hide a link or FIFO.
                if root / relative == excluded:
                    continue
                size, digest = _file_digest(directory_fd, name)
                entries.append({"path": relative, "size": size, "sha256": digest})
    except OSError as exc:
        raise ManifestError("bundle input unavailable") from exc
    finally:
        for directory_fd, _, _ in reversed(stack):
            os.close(directory_fd)
    return {"schema": SCHEMA, "files": sorted(entries, key=lambda entry: entry["path"])}


def compare_manifests(before, after):
    """Compare validated path/size/digest records; omit unchanged entries."""
    old = _validated(before)
    new = _validated(after)
    return {
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "changed": sorted(path for path in old.keys() & new.keys() if old[path] != new[path]),
    }


def _output_path(destination, relative):
    relative = _relative_path(relative)
    destination = _directory(destination)
    output = destination.joinpath(*PurePosixPath(relative).parts)
    _directory(output.parent)
    try:
        info = output.lstat()
    except FileNotFoundError:
        return output
    _regular(info)
    return output


def _write_manifest(output, payload):
    """Write only the explicitly selected manifest; reject existing payloads."""
    parent_fd = _open_directory(output.parent)
    try:
        flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
        try:
            descriptor = os.open(output.name, flags | os.O_CREAT | os.O_EXCL, _OUTPUT_MODE,
                                 dir_fd=parent_fd)
            created = True
        except FileExistsError:
            descriptor = os.open(output.name, flags, dir_fd=parent_fd)
            created = False
        with os.fdopen(descriptor, "r+b") as target:
            _regular(os.fstat(target.fileno()))
            if not created:
                load_manifest(target.read())
            target.seek(0)  # Offset zero denotes the beginning of the output file.
            target.write(payload)
            target.truncate()
    finally:
        os.close(parent_fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inventory", help="inventory regular-file bytes")
    inspect.add_argument("bundle", type=Path)
    inspect.add_argument("--destination", type=Path)
    inspect.add_argument("--output", help="relative manifest path; requires --destination")
    compare = commands.add_parser("compare", help="compare two strict JSON manifests")
    compare.add_argument("before", type=Path)
    compare.add_argument("after", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            if args.output is not None and args.destination is None:
                raise ManifestError("output requires a destination")
            output = (_output_path(args.destination,
                                   args.output if args.output is not None else "manifest.json")
                      if args.destination is not None else None)
            result = inventory(args.bundle, exclude_output=output)
            payload = serialize_manifest(result)
            if output is not None:
                _write_manifest(output, payload)
            else:
                sys.stdout.buffer.write(payload)
            return 0
        before = read_manifest(args.before)
        after = read_manifest(args.after)
        result = compare_manifests(before, after)
        sys.stdout.buffer.write(_json_bytes(result))
        return 1 if any(result.values()) else 0
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
    except OSError:
        print("error: filesystem input or output unavailable", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
