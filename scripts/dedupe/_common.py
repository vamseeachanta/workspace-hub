"""Shared validation and atomic writes.

Format and performance conventions are specified in README.md, Schema (issue #4224).
Atomic replacement follows Python 3.11 os.replace documentation.
"""

import json
import os
import stat
import tempfile
from pathlib import Path

FORMAT_VERSION = 1  # README.md, Schema: initial application format, not a limit.


def json_text(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)


def atomic_write_output(destination, text):
    """The sole allowed replacement: a tool-owned temporary output, never scan data.

    Failed writes intentionally retain the temporary output for diagnosis.
    """
    destination = Path(destination)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=destination.parent,
        prefix=destination.name + ".",
        suffix=".partial",
        delete=False,
    ) as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
        temporary_output = stream.name
    os.replace(temporary_output, destination)  # Only tool-owned output replacement.


def distinct_outputs(outputs, inputs=(), roots=()):
    """Reject input overwrite, scan-root writes and output aliases before any write."""
    outputs = [Path(p) for p in outputs if p is not None]
    inputs = [Path(p) for p in inputs]
    roots = [Path(p).resolve() for p in roots]
    for index, output in enumerate(outputs):
        resolved = output.resolve()
        absolute = output.absolute()
        if any(resolved.is_relative_to(r) or absolute.is_relative_to(r) for r in roots):
            raise ValueError("outputs must be outside scanned roots")
        for other in inputs + outputs[:index]:
            if resolved == other.resolve() or (
                output.exists() and other.exists() and output.samefile(other)
            ):
                raise ValueError("outputs must be distinct from inputs and each other")
        if output.exists() and roots:
            # An output outside a root may still be a hard link to scanned data.
            identity = output.stat()
            for root in roots:
                for folder, directories, names in os.walk(root, followlinks=False):
                    directories[:] = [
                        name for name in directories
                        if not is_reparse_point((Path(folder) / name).lstat())
                        and not (Path(folder) / name).is_symlink()
                    ]
                    for name in names:
                        candidate = Path(folder) / name
                        info = candidate.stat(follow_symlinks=False)
                        if (info.st_dev, info.st_ino) == (
                            identity.st_dev,
                            identity.st_ino,
                        ):
                            raise ValueError("output aliases scanned data")


def is_reparse_point(info):
    """Treat Windows junctions and other reparse points as links."""
    return bool(
        getattr(info, "st_file_attributes", 0)
        & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def read_json(path):
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def valid_digest(value):
    # FIPS 180-4 (2015), section 6.2: 256 bits / 4 bits per hex digit = 64.
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def validate_record(row):
    """Validate evidence structure before merge or planning; paths stay relative."""
    if not isinstance(row, dict):
        raise TypeError("file record must be an object")
    if not isinstance(row.get("label"), str) or not row["label"].strip():
        raise ValueError("invalid label")
    # Manifest paths use POSIX separators; colons and backslashes are literal
    # filename characters, never native paths to resolve on the reading system.
    path = row.get("path")
    if (
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or "\0" in path
        or any(part in ("", ".", "..") for part in path.split("/"))
    ):
        raise ValueError("invalid relative path")
    for field in ("root", "size"):
        if field == "size" and "error" in row and row.get(field) is None:
            continue
        if type(row.get(field)) is not int or row[field] < 0:
            raise ValueError("invalid nonnegative integer")
    if "error" in row and row.get("mtime") is None:
        if row.get("sha256") is not None or row.get("stage") != "size":
            raise ValueError("metadata error cannot carry full evidence")
        return
    if type(row.get("mtime")) is not int:
        raise ValueError("mtime must be integer nanoseconds")
    stage = row.get("stage")
    if stage not in ("size", "sample", "full"):
        raise ValueError("invalid hash stage")
    digest = row.get("sha256")
    sample = row.get("sample_sha256")
    if sample is not None and not valid_digest(sample):
        raise ValueError("invalid sample hash")
    if digest is not None and (not valid_digest(digest) or stage != "full"):
        raise ValueError("invalid full hash evidence")
    if stage == "full" and (digest is None or sample is None):
        raise ValueError("full stage requires both hashes")
    if stage == "sample" and sample is None:
        raise ValueError("sample stage requires sample hash")


def identity(row):
    return row["label"], row["root"], row["path"]
