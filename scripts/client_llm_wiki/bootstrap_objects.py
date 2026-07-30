"""Exact Git object construction for client-wiki finalization."""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath

from .bootstrap_snapshot import TemplateMember


def object_oid(algorithm: str, kind: str, data: bytes) -> str:
    framed = f"{kind} {len(data)}\0".encode() + data
    return hashlib.new(algorithm, framed).hexdigest()


def expected_tree(algorithm: str, members: tuple[TemplateMember, ...]) -> str:
    if algorithm not in {"sha1", "sha256"}:
        raise ValueError("repository object format is unsupported")
    blobs = {
        member.path: (member.mode, object_oid(algorithm, "blob", member.data))
        for member in members if member.data is not None
    }
    return _expected_subtree(algorithm, blobs, "")


def _expected_subtree(
    algorithm: str, blobs: dict[str, tuple[int, str]], prefix: str,
) -> str:
    entries: list[tuple[bytes, bytes]] = []
    directories = sorted({
        PurePosixPath(path[len(prefix):]).parts[0]
        for path in blobs if path.startswith(prefix) and "/" in path[len(prefix):]
    })
    for name in directories:
        oid = _expected_subtree(algorithm, blobs, f"{prefix}{name}/")
        raw = b"40000 " + name.encode() + b"\0" + bytes.fromhex(oid)
        entries.append((name.encode() + b"/", raw))
    for path, (mode, oid) in blobs.items():
        suffix = path[len(prefix):] if path.startswith(prefix) else path
        if "/" not in suffix:
            name = suffix.encode()
            raw = f"{mode:o} ".encode() + name + b"\0" + bytes.fromhex(oid)
            entries.append((name, raw))
    data = b"".join(value for _, value in sorted(entries))
    return object_oid(algorithm, "tree", data)
