"""Bounded atomic evidence for a descriptor-bound client-wiki render."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any

from .bootstrap_renderer import BoundClone


class BootstrapManifestError(RuntimeError):
    """The external manifest or independently observed render is unsafe."""


@dataclass(frozen=True, slots=True)
class ManifestIdentity:
    device: int
    inode: int
    file_type: int


@dataclass(frozen=True, slots=True)
class PersistedRenderManifest:
    bytes: bytes
    identities: dict[str, ManifestIdentity]
    final_identity: ManifestIdentity


@dataclass(frozen=True, slots=True)
class _ExpectedRender:
    identities: dict[str, ManifestIdentity]
    members: dict[str, Any]
    memberships: dict[str, list[str]]


_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
_CREATE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
_MAX_MANIFEST_BYTES = 8 * 1024 * 1024
_MAX_MEMBERS = 8192
_MAX_DEPTH = 32
_FIREWALL = (".claude/CLAUDE.md", ".gitignore")


def _identity(info: os.stat_result) -> ManifestIdentity:
    return ManifestIdentity(info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode))


def _identity_json(identity: ManifestIdentity) -> dict[str, int]:
    return {
        "device": identity.device,
        "inode": identity.inode,
        "type": identity.file_type,
    }


def _read_all(descriptor: int, limit: int = _MAX_MANIFEST_BYTES) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, min(65536, limit + 1 - total))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
        if total > limit:
            raise BootstrapManifestError("manifest or rendered file exceeds size limit")


def _hash_file(parent_fd: int, name: str) -> tuple[int, str]:
    descriptor = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise BootstrapManifestError("rendered member is not a regular file")
        digest = hashlib.sha256()
        size = 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                return size, digest.hexdigest()
            size += len(chunk)
            if size > _MAX_MANIFEST_BYTES:
                raise BootstrapManifestError("rendered file exceeds size limit")
            digest.update(chunk)
    finally:
        os.close(descriptor)


def _member_record(parent_fd: int, name: str, info: os.stat_result) -> dict[str, Any]:
    mode = stat.S_IMODE(info.st_mode)
    if stat.S_ISDIR(info.st_mode):
        return {"type": "directory", "mode": mode, "size": 0, "sha256": None}
    if not stat.S_ISREG(info.st_mode):
        raise BootstrapManifestError("rendered member has unsupported type")
    size, digest = _hash_file(parent_fd, name)
    if size != info.st_size:
        raise BootstrapManifestError("rendered member changed while hashing")
    return {"type": "file", "mode": mode, "size": size, "sha256": digest}


def _scan_directory(
    descriptor: int, relative: str, members: dict[str, Any], memberships: dict[str, list[str]], depth: int,
) -> None:
    if depth > _MAX_DEPTH:
        raise BootstrapManifestError("rendered tree exceeds depth limit")
    names = sorted(os.listdir(descriptor))
    memberships[relative] = names
    for name in names:
        if relative == "" and name == ".git":
            continue
        path = str(PurePosixPath(relative) / name) if relative else name
        if len(members) >= _MAX_MEMBERS:
            raise BootstrapManifestError("rendered tree exceeds member limit")
        info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        members[path] = _member_record(descriptor, name, info)
        if stat.S_ISDIR(info.st_mode):
            child = os.open(name, _DIR_FLAGS, dir_fd=descriptor)
            try:
                if _identity(os.fstat(child)) != _identity(info):
                    raise BootstrapManifestError("rendered directory identity changed")
                _scan_directory(child, path, members, memberships, depth + 1)
            finally:
                os.close(child)


def _snapshot_clone(clone: BoundClone) -> tuple[dict[str, Any], dict[str, list[str]]]:
    members: dict[str, Any] = {}
    memberships: dict[str, list[str]] = {}
    _scan_directory(clone.root_fd, "", members, memberships, 0)
    for firewall in _FIREWALL:
        record = members.get(firewall)
        if record is None or record["type"] != "file" or record["mode"] != 0o644:
            raise BootstrapManifestError("privacy firewall is missing or invalid")
    return members, memberships


def _open_config(clone: BoundClone) -> tuple[int, ManifestIdentity]:
    descriptor = os.open("config", _FILE_FLAGS, dir_fd=clone.git_fd)
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode):
        os.close(descriptor)
        raise BootstrapManifestError(".git/config must be a regular file")
    return descriptor, _identity(info)


def _open_manifest_parent(destination: Path) -> tuple[int, ManifestIdentity]:
    try:
        descriptor = os.open(destination.parent, _DIR_FLAGS)
    except OSError as exc:
        raise BootstrapManifestError("manifest parent must be a real directory") from exc
    return descriptor, _identity(os.fstat(descriptor))


def _reject_inside_target(parent_fd: int, clone: BoundClone) -> None:
    current = os.dup(parent_fd)
    try:
        for _ in range(256):
            identity = _identity(os.fstat(current))
            if identity == ManifestIdentity(clone.root_id.device, clone.root_id.inode, clone.root_id.file_type):
                raise BootstrapManifestError("manifest must be outside the target clone")
            ancestor = os.open("..", _DIR_FLAGS, dir_fd=current)
            ancestor_id = _identity(os.fstat(ancestor))
            if ancestor_id == identity:
                os.close(ancestor)
                return
            os.close(current)
            current = ancestor
        raise BootstrapManifestError("manifest parent ancestry exceeds limit")
    finally:
        os.close(current)


def _check_existing(parent_fd: int, name: str) -> None:
    try:
        descriptor = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise BootstrapManifestError("manifest final entry is unsafe") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise BootstrapManifestError("manifest placeholder must be regular mode 0600")
    finally:
        os.close(descriptor)


def _bound_identities(
    clone: BoundClone, config_id: ManifestIdentity, manifest_parent_id: ManifestIdentity,
) -> dict[str, ManifestIdentity]:
    root = ManifestIdentity(clone.root_id.device, clone.root_id.inode, clone.root_id.file_type)
    git = ManifestIdentity(clone.git_id.device, clone.git_id.inode, clone.git_id.file_type)
    return {
        "parent": _identity(os.fstat(clone.parent_fd)), "root": root, "git": git,
        "config": config_id, "manifest_parent": manifest_parent_id,
    }


def _document(
    identities: dict[str, ManifestIdentity], members: dict[str, Any],
    memberships: dict[str, list[str]], repo: str, origins: tuple[str, ...], commit: str, tree: str,
) -> bytes:
    payload = {
        "version": 1, "registered_repo": repo, "allowed_origins": list(origins),
        "template": {"commit": commit, "tree": tree},
        "identities": {name: _identity_json(value) for name, value in identities.items()},
        "members": members, "memberships": memberships, "firewall": list(_FIREWALL),
    }
    encoded = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(encoded) > _MAX_MANIFEST_BYTES:
        raise BootstrapManifestError("manifest exceeds size limit")
    return encoded


def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise BootstrapManifestError("manifest write made no progress")
        offset += written


def _after_operation(_stage: str) -> None:
    """Internal test seam; production callers cannot supply operations."""


def _validate_render_state(clone: BoundClone, parent_fd: int, expected: _ExpectedRender) -> None:
    config_fd, config_id = _open_config(clone)
    try:
        identities = _bound_identities(clone, config_id, _identity(os.fstat(parent_fd)))
        members, memberships = _snapshot_clone(clone)
        if identities != expected.identities:
            raise BootstrapManifestError("bound identity substitution detected")
        if members != expected.members or memberships != expected.memberships:
            raise BootstrapManifestError("rendered content substitution detected")
    finally:
        os.close(config_fd)


def _publish(
    clone: BoundClone, parent_fd: int, name: str, data: bytes, expected: _ExpectedRender,
) -> ManifestIdentity:
    temp_name = f".{name}.tmp-{os.getpid()}-{os.urandom(8).hex()}"
    descriptor = os.open(temp_name, _CREATE_FLAGS, 0o600, dir_fd=parent_fd)
    try:
        _write_all(descriptor, data)
        os.fchmod(descriptor, 0o600)
        os.fdatasync(descriptor)
        _after_operation("temp_synced")
        _validate_render_state(clone, parent_fd, expected)
    finally:
        os.close(descriptor)
    os.replace(temp_name, name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    os.fsync(parent_fd)
    _after_operation("published")
    _validate_render_state(clone, parent_fd, expected)
    final_fd = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
    try:
        info = os.fstat(final_fd)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise BootstrapManifestError("published manifest type or mode changed")
        if _read_all(final_fd) != data:
            raise BootstrapManifestError("published manifest bytes changed")
        return _identity(info)
    finally:
        os.close(final_fd)


def persist_render_manifest(
    clone: BoundClone, destination: Path, *, registered_repo: str,
    allowed_origins: tuple[str, ...], template_commit: str, template_tree: str,
) -> PersistedRenderManifest:
    """Atomically publish complete evidence through held descriptors."""
    destination = Path(destination).absolute()
    parent_fd = config_fd = -1
    try:
        parent_fd, parent_id = _open_manifest_parent(destination)
        _reject_inside_target(parent_fd, clone)
        _check_existing(parent_fd, destination.name)
        config_fd, config_id = _open_config(clone)
        identities = _bound_identities(clone, config_id, parent_id)
        members, memberships = _snapshot_clone(clone)
        data = _document(
            identities, members, memberships, registered_repo,
            tuple(sorted(allowed_origins)), template_commit, template_tree,
        )
        expected = _ExpectedRender(identities, members, memberships)
        final_id = _publish(clone, parent_fd, destination.name, data, expected)
        result = PersistedRenderManifest(data, identities, final_id)
        _validate_bound(clone, parent_fd, destination.name, result)
        return result
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise BootstrapManifestError("manifest publication failed") from exc
    finally:
        for descriptor in (config_fd, parent_fd):
            if descriptor >= 0:
                os.close(descriptor)


def _validate_bound(
    clone: BoundClone, parent_fd: int, name: str, expected: PersistedRenderManifest,
) -> None:
    config_fd, config_id = _open_config(clone)
    try:
        identities = _bound_identities(clone, config_id, _identity(os.fstat(parent_fd)))
        if identities != expected.identities:
            raise BootstrapManifestError("bound identity substitution detected")
        members, memberships = _snapshot_clone(clone)
        payload = json.loads(expected.bytes)
        if members != payload["members"] or memberships != payload["memberships"]:
            raise BootstrapManifestError("rendered content differs from manifest evidence")
        final_fd = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
        try:
            info = os.fstat(final_fd)
            if _identity(info) != expected.final_identity or stat.S_IMODE(info.st_mode) != 0o600:
                raise BootstrapManifestError("final manifest entry substitution detected")
            if _read_all(final_fd) != expected.bytes:
                raise BootstrapManifestError("final manifest bytes differ")
        finally:
            os.close(final_fd)
    finally:
        os.close(config_fd)


def validate_render_manifest(
    target: Path, destination: Path, expected: PersistedRenderManifest,
) -> None:
    """Independently bind and enumerate target and external evidence."""
    destination = Path(destination).absolute()
    parent_fd = -1
    try:
        parent_fd, _ = _open_manifest_parent(destination)
        with _bind_populated_clone(Path(target)) as clone:
            _reject_inside_target(parent_fd, clone)
            _validate_bound(clone, parent_fd, destination.name, expected)
    finally:
        if parent_fd >= 0:
            os.close(parent_fd)


class _bind_populated_clone:
    def __init__(self, target: Path):
        self.target = target
        self.fds: list[int] = []

    def __enter__(self) -> BoundClone:
        parent = os.open(self.target.parent, _DIR_FLAGS)
        root = os.open(self.target.name, _DIR_FLAGS, dir_fd=parent)
        git = os.open(".git", _DIR_FLAGS, dir_fd=root)
        self.fds = [git, root, parent]
        return BoundClone(
            self.target, self.target.name, parent, root, git,
            _to_file_identity(os.fstat(root)), _to_file_identity(os.fstat(git)),
        )

    def __exit__(self, *_args: object) -> None:
        for descriptor in self.fds:
            os.close(descriptor)


def _to_file_identity(info: os.stat_result):
    from .bootstrap_renderer import FileIdentity

    return FileIdentity(info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode))
