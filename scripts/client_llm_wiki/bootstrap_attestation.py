"""Descriptor-first bounded render-tree scanning for manifest attestation."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import os
from pathlib import PurePosixPath
import stat
from typing import Any
class BootstrapManifestError(RuntimeError):
    def __init__(self, message: str, *, backing_name: str | None = None):
        super().__init__(message)
        self.backing_name = backing_name
@dataclass(frozen=True, slots=True)
class ManifestIdentity:
    device: int
    inode: int
    file_type: int
@dataclass(slots=True)
class _Budget:
    members: int = 0
    path_bytes: int = 0
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
MAX_RENDER_BYTES = 64 * 1024 * 1024
MAX_MEMBERS = 8192
MAX_PATH_BYTES = 1024 * 1024
MAX_DEPTH = 32
FIREWALL = (".claude/CLAUDE.md", ".gitignore")
def identity(info: os.stat_result) -> ManifestIdentity:
    return ManifestIdentity(info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode))
def read_digest(descriptor: int, limit: int) -> tuple[int, str, bytes]:
    os.lseek(descriptor, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = os.read(descriptor, min(65536, limit + 1 - size))
        if not chunk:
            return size, digest.hexdigest(), b"".join(chunks)
        size += len(chunk)
        if size > limit:
            raise BootstrapManifestError("bounded file read exceeded")
        digest.update(chunk)
        chunks.append(chunk)
def stable_digest(descriptor: int, before: os.stat_result, limit: int) -> tuple[int, str, bytes]:
    size, digest, data = read_digest(descriptor, limit)
    after = os.fstat(descriptor)
    stable = (
        identity(after) == identity(before)
        and stat.S_IMODE(after.st_mode) == stat.S_IMODE(before.st_mode)
        and after.st_size == before.st_size == size
        and after.st_mtime_ns == before.st_mtime_ns
        and after.st_ctime_ns == before.st_ctime_ns
        and after.st_nlink == before.st_nlink
    )
    if not stable:
        raise BootstrapManifestError("file changed while being attested")
    return size, digest, data
def _claim_name(relative: str, name: str, budget: _Budget) -> str:
    if not name or name in {".", ".."} or "/" in name or "\0" in name:
        raise BootstrapManifestError("rendered member name is unsafe")
    path = str(PurePosixPath(relative) / name) if relative else name
    budget.members += 1
    budget.path_bytes += len(path.encode("utf-8"))
    if budget.members > MAX_MEMBERS:
        raise BootstrapManifestError("rendered tree exceeds member limit")
    if budget.path_bytes > MAX_PATH_BYTES:
        raise BootstrapManifestError("rendered tree exceeds path limit")
    return path
def _stream_names(descriptor: int, relative: str, budget: _Budget, *, claim: bool) -> list[str]:
    names: list[str] = []
    with os.scandir(descriptor) as entries:
        for entry in entries:
            if claim and not (relative == "" and entry.name == ".git"):
                _claim_name(relative, entry.name, budget)
            names.append(entry.name)
            if len(names) > MAX_MEMBERS + 1:
                raise BootstrapManifestError("directory membership exceeds limit")
    return sorted(names)
def _open_member(parent_fd: int, name: str) -> tuple[int, bool]:
    try:
        return os.open(name, _DIR_FLAGS, dir_fd=parent_fd), True
    except NotADirectoryError:
        try:
            return os.open(name, _FILE_FLAGS, dir_fd=parent_fd), False
        except OSError as exc:
            raise BootstrapManifestError("rendered member cannot be opened no-follow") from exc
    except OSError as exc:
        raise BootstrapManifestError("rendered member cannot be opened no-follow") from exc
def after_member_scan(_path: str, _is_directory: bool) -> None:
    """Private member-race test seam."""
def _verify_parent_entry(
    parent_fd: int, name: str, descriptor: int, before: os.stat_result, is_directory: bool,
) -> None:
    named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    reopened, reopened_directory = _open_member(parent_fd, name)
    try:
        current, again = os.fstat(descriptor), os.fstat(reopened)
        expected = (identity(before), stat.S_IMODE(before.st_mode), before.st_size)
        observations = [
            (identity(info), stat.S_IMODE(info.st_mode), info.st_size)
            for info in (current, named, again)
        ]
        if reopened_directory != is_directory or any(item != expected for item in observations):
            raise BootstrapManifestError("parent entry no longer names held member")
    finally:
        os.close(reopened)
def _scan_member(
    parent_fd: int, name: str, path: str, members: dict[str, Any],
    memberships: dict[str, list[str]], budget: _Budget, depth: int,
) -> None:
    descriptor, is_directory = _open_member(parent_fd, name)
    try:
        before = os.fstat(descriptor)
        mode = stat.S_IMODE(before.st_mode)
        if is_directory:
            members[path] = {"type": "directory", "mode": mode, "size": 0, "sha256": None}
            _scan_directory(descriptor, path, members, memberships, budget, depth + 1)
        else:
            if not stat.S_ISREG(before.st_mode):
                raise BootstrapManifestError("rendered member has unsupported type")
            size, digest, _ = stable_digest(descriptor, before, MAX_RENDER_BYTES)
            members[path] = {"type": "file", "mode": mode, "size": size, "sha256": digest}
        after = os.fstat(descriptor)
        stable = (
            identity(after) == identity(before)
            and stat.S_IMODE(after.st_mode) == stat.S_IMODE(before.st_mode)
            and after.st_size == before.st_size
        )
        if not stable:
            raise BootstrapManifestError("rendered member identity/mode/size changed")
        after_member_scan(path, is_directory)
        _verify_parent_entry(parent_fd, name, descriptor, before, is_directory)
    finally:
        os.close(descriptor)
def _scan_directory(
    descriptor: int, relative: str, members: dict[str, Any],
    memberships: dict[str, list[str]], budget: _Budget, depth: int,
) -> None:
    if depth > MAX_DEPTH:
        raise BootstrapManifestError("rendered tree exceeds depth limit")
    names = _stream_names(descriptor, relative, budget, claim=True)
    memberships[relative] = names
    for name in names:
        if relative == "" and name == ".git":
            continue
        path = str(PurePosixPath(relative) / name) if relative else name
        _scan_member(descriptor, name, path, members, memberships, budget, depth)
    if _stream_names(descriptor, relative, budget, claim=False) != names:
        raise BootstrapManifestError("directory membership changed during enumeration")
def snapshot_clone(root_fd: int) -> tuple[dict[str, Any], dict[str, list[str]]]:
    members: dict[str, Any] = {}
    memberships: dict[str, list[str]] = {}
    _scan_directory(root_fd, "", members, memberships, _Budget(), 0)
    for path in FIREWALL:
        record = members.get(path)
        if record is None or record["type"] != "file" or record["mode"] != 0o644:
            raise BootstrapManifestError("privacy firewall is missing or invalid")
    return members, memberships
