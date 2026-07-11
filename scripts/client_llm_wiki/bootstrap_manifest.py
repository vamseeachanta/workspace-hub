"""No-replace publication and independent attestation of render evidence."""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
from typing import Any
from . import bootstrap_attestation as attestation
from .bootstrap_attestation import (
    BootstrapManifestError, FIREWALL as _FIREWALL,
    ManifestIdentity, identity as _identity, stable_digest as _stable_digest,
)
from .bootstrap_git import BootstrapGitError, accepted_origins, validate_clone_git
from .bootstrap_layout import BoundCloneLayout
from .bootstrap_renderer import BoundClone, FileIdentity
@dataclass(frozen=True, slots=True)
class PersistedRenderManifest:
    bytes: bytes
    backing_name: str
@dataclass(frozen=True, slots=True)
class _ExpectedRender:
    identities: dict[str, ManifestIdentity]
    config: dict[str, Any]
    members: dict[str, Any]
    memberships: dict[str, list[str]]
    metadata: dict[str, Any]
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
_CREATE_FLAGS = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
_MAX_MANIFEST_BYTES = 8 * 1024 * 1024
_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
def _identity_json(value: ManifestIdentity) -> dict[str, int]:
    return {"device": value.device, "inode": value.inode, "type": value.file_type}
def _snapshot_clone(clone: BoundClone) -> tuple[dict[str, Any], dict[str, list[str]]]:
    return attestation.snapshot_clone(clone.root_fd)
def _open_config(clone: BoundClone) -> int:
    descriptor = os.open("config", _FILE_FLAGS, dir_fd=clone.git_fd)
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise BootstrapManifestError(".git/config must be regular")
    return descriptor
def _config_evidence(clone: BoundClone, descriptor: int, repo: str) -> dict[str, Any]:
    before = os.fstat(descriptor)
    layout = BoundCloneLayout(clone.root_fd, clone.git_fd, descriptor)
    try:
        parsed = validate_clone_git(layout, repo)
    except BootstrapGitError as exc:
        raise BootstrapManifestError("clone config/origin semantics are invalid") from exc
    size, digest, _ = _stable_digest(descriptor, before, _MAX_MANIFEST_BYTES)
    return {"mode": stat.S_IMODE(before.st_mode), "size": size, "sha256": digest, "parsed": parsed}
def _clone_identities(
    clone: BoundClone, config_fd: int, manifest_parent: ManifestIdentity,
) -> dict[str, ManifestIdentity]:
    parent, root, git = map(_identity, map(os.fstat, (clone.parent_fd, clone.root_fd, clone.git_fd)))
    named_root = _identity(os.stat(clone.basename, dir_fd=clone.parent_fd, follow_symlinks=False))
    named_git = _identity(os.stat(".git", dir_fd=clone.root_fd, follow_symlinks=False))
    if named_root != root or named_git != git:
        raise BootstrapManifestError("clone identity substitution detected")
    return {
        "parent": parent, "root": root, "git": git,
        "config": _identity(os.fstat(config_fd)), "manifest_parent": manifest_parent,
    }
def _metadata(
    repo: str, origins: tuple[str, ...], commit: str, tree: str, backing: str,
) -> dict[str, Any]:
    try:
        canonical = tuple(sorted(accepted_origins(repo)))
    except BootstrapGitError as exc:
        raise BootstrapManifestError("registered repository is invalid") from exc
    if tuple(sorted(origins)) != canonical or not _OID.fullmatch(commit) or not _OID.fullmatch(tree):
        raise BootstrapManifestError("manifest authority metadata is invalid")
    return {
        "registered_repo": repo, "allowed_origins": list(canonical),
        "template": {"commit": commit, "tree": tree}, "firewall": list(_FIREWALL),
        "backing_name": backing,
    }
def _document(expected: _ExpectedRender) -> bytes:
    payload = {
        "version": 1, **expected.metadata,
        "identities": {key: _identity_json(value) for key, value in expected.identities.items()},
        "config": expected.config, "members": expected.members, "memberships": expected.memberships,
    }
    data = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(data) > _MAX_MANIFEST_BYTES:
        raise BootstrapManifestError("manifest exceeds size limit")
    return data
def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise BootstrapManifestError("manifest write made no progress")
        offset += written
def _after_operation(_stage: str) -> None:
    """Private fixed-stage test seam."""
def _before_return() -> None:
    """Private final-boundary test seam."""
def _after_link_read(_index: int) -> None:
    """Private hard-link read-race test seam."""
def _open_parent(destination: Path) -> tuple[int, ManifestIdentity]:
    try:
        descriptor = os.open(destination.parent, _DIR_FLAGS)
    except OSError as exc:
        raise BootstrapManifestError("manifest parent must be a real directory") from exc
    return descriptor, _identity(os.fstat(descriptor))
def _reject_inside(parent_fd: int, clone: BoundClone) -> None:
    current = os.dup(parent_fd)
    root = _identity(os.fstat(clone.root_fd))
    try:
        for _ in range(256):
            identity = _identity(os.fstat(current))
            if identity == root:
                raise BootstrapManifestError("manifest must be outside target")
            ancestor = os.open("..", _DIR_FLAGS, dir_fd=current)
            if _identity(os.fstat(ancestor)) == identity:
                os.close(ancestor)
                return
            os.close(current)
            current = ancestor
        raise BootstrapManifestError("manifest ancestry exceeds limit")
    finally:
        os.close(current)
def _require_absent(parent_fd: int, name: str) -> None:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise BootstrapManifestError("manifest final entry must be absent")
def _validate_state(clone: BoundClone, parent_fd: int, expected: _ExpectedRender) -> None:
    config_fd = _open_config(clone)
    try:
        identities = _clone_identities(clone, config_fd, _identity(os.fstat(parent_fd)))
        config = _config_evidence(clone, config_fd, expected.metadata["registered_repo"])
        members, memberships = _snapshot_clone(clone)
        if (identities, config, members, memberships) != (
            expected.identities, expected.config, expected.members, expected.memberships,
        ):
            raise BootstrapManifestError("independent render attestation differs")
    finally:
        os.close(config_fd)
def _verify_links(
    parent_fd: int, final: str, backing: str, data: bytes,
) -> ManifestIdentity:
    descriptors: list[int] = []
    try:
        for name in (final, backing):
            descriptors.append(os.open(name, _FILE_FLAGS, dir_fd=parent_fd))
        before = [os.fstat(fd) for fd in descriptors]
        contents: list[bytes] = []
        for index, descriptor in enumerate(descriptors):
            contents.append(_stable_digest(descriptor, before[index], _MAX_MANIFEST_BYTES)[2])
            _after_link_read(index)
        infos = [os.fstat(fd) for fd in descriptors]
        identities = [_identity(info) for info in infos]
        valid = (
            identities[0] == identities[1] and infos[0].st_nlink == infos[1].st_nlink == 2
            and all(stat.S_IMODE(info.st_mode) == 0o600 for info in infos)
            and all(info.st_size == len(data) for info in infos)
            and all(content == data for content in contents)
            and all(info.st_mtime_ns == old.st_mtime_ns and info.st_ctime_ns == old.st_ctime_ns
                    for info, old in zip(infos, before, strict=True))
        )
        if not valid:
            raise BootstrapManifestError("manifest hard-link publication is invalid")
        return identities[0]
    finally:
        for descriptor in descriptors:
            os.close(descriptor)
def _sync_backing(
    clone: BoundClone, parent_fd: int, backing: str, data: bytes,
    expected: _ExpectedRender,
) -> None:
    descriptor = os.open(backing, _CREATE_FLAGS, 0o600, dir_fd=parent_fd)
    try:
        _write_all(descriptor, data)
        os.fchmod(descriptor, 0o600)
        os.fdatasync(descriptor)
        _after_operation("backing_synced")
        _validate_state(clone, parent_fd, expected)
    finally:
        os.close(descriptor)

def _publish(
    clone: BoundClone, parent_fd: int, final: str, backing: str,
    data: bytes, expected: _ExpectedRender,
) -> tuple[ManifestIdentity, str]:
    try:
        _sync_backing(clone, parent_fd, backing, data, expected)
        os.link(backing, final, src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False)
        os.fsync(parent_fd)
        _after_operation("published")
        _validate_state(clone, parent_fd, expected)
        return _verify_links(parent_fd, final, backing, data), backing
    except BaseException as exc:
        if isinstance(exc, BootstrapManifestError):
            exc.backing_name = backing
            raise
        raise BootstrapManifestError("manifest no-replace publication failed", backing_name=backing) from exc
def persist_render_manifest(
    clone: BoundClone, destination: Path, *, registered_repo: str,
    allowed_origins: tuple[str, ...], template_commit: str, template_tree: str,
) -> PersistedRenderManifest:
    destination = Path(destination).absolute()
    parent_fd = config_fd = -1
    backing: str | None = None
    try:
        parent_fd, parent_id = _open_parent(destination)
        _reject_inside(parent_fd, clone)
        _require_absent(parent_fd, destination.name)
        config_fd = _open_config(clone)
        backing = f".{destination.name}.backing-{os.getpid()}-{os.urandom(8).hex()}"
        metadata = _metadata(
            registered_repo, allowed_origins, template_commit, template_tree, backing,
        )
        expected = _ExpectedRender(
            _clone_identities(clone, config_fd, parent_id),
            _config_evidence(clone, config_fd, registered_repo),
            *_snapshot_clone(clone), metadata,
        )
        data = _document(expected)
        _final_id, backing = _publish(
            clone, parent_fd, destination.name, backing, data, expected,
        )
        result = PersistedRenderManifest(data, backing)
        _before_return()
        _validate_bound(
            clone, parent_fd, destination.name, registered_repo, allowed_origins,
            template_commit, template_tree,
        )
        return result
    except BootstrapManifestError:
        raise
    except BaseException as exc:
        raise BootstrapManifestError("manifest persistence failed", backing_name=backing) from exc
    finally:
        for descriptor in (config_fd, parent_fd):
            if descriptor >= 0:
                os.close(descriptor)
def _strict_json(data: bytes) -> dict[str, Any]:
    def pairs(items):
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise BootstrapManifestError("manifest contains duplicate keys")
            result[key] = value
        return result
    payload = json.loads(data, object_pairs_hook=pairs)
    if not isinstance(payload, dict):
        raise BootstrapManifestError("manifest JSON must be an object")
    return payload
def _read_claims(parent_fd: int, final: str) -> tuple[dict[str, Any], bytes]:
    descriptor = os.open(final, _FILE_FLAGS, dir_fd=parent_fd)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or stat.S_IMODE(before.st_mode) != 0o600:
            raise BootstrapManifestError("manifest final entry is unsafe")
        data = _stable_digest(descriptor, before, _MAX_MANIFEST_BYTES)[2]
        return _strict_json(data), data
    finally:
        os.close(descriptor)
def _trusted_expected(
    clone: BoundClone, parent_fd: int, repo: str, origins: tuple[str, ...],
    commit: str, tree: str, backing: str,
) -> _ExpectedRender:
    config_fd = _open_config(clone)
    try:
        return _ExpectedRender(
            _clone_identities(clone, config_fd, _identity(os.fstat(parent_fd))),
            _config_evidence(clone, config_fd, repo), *_snapshot_clone(clone),
            _metadata(repo, origins, commit, tree, backing),
        )
    finally:
        os.close(config_fd)
def _validate_bound(
    clone: BoundClone, parent_fd: int, final: str, repo: str, origins: tuple[str, ...],
    commit: str, tree: str,
) -> None:
    claims, data = _read_claims(parent_fd, final)
    backing = claims.get("backing_name")
    prefix = f".{final}.backing-"
    pattern = re.escape(prefix) + r"[0-9]+-[0-9a-f]{16}"
    if not isinstance(backing, str) or re.fullmatch(pattern, backing) is None:
        raise BootstrapManifestError("manifest backing claim is invalid")
    expected = _trusted_expected(clone, parent_fd, repo, origins, commit, tree, backing)
    if claims != _strict_json(_document(expected)) or data != _document(expected):
        raise BootstrapManifestError("untrusted manifest claims differ")
    _verify_links(parent_fd, final, backing, data)
    _validate_state(clone, parent_fd, expected)
def validate_render_manifest(
    target: Path, destination: Path, registered_repo: str, allowed_origins: tuple[str, ...],
    template_commit: str, template_tree: str,
) -> None:
    parent_fd = -1
    try:
        parent_fd, _ = _open_parent(Path(destination).absolute())
        with _bind_populated_clone(Path(target)) as clone:
            _reject_inside(parent_fd, clone)
            _validate_bound(
                clone, parent_fd, Path(destination).name, registered_repo,
                allowed_origins, template_commit, template_tree,
            )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, BootstrapGitError) as exc:
        raise BootstrapManifestError("manifest validation failed") from exc
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
            _file_identity(os.fstat(root)), _file_identity(os.fstat(git)),
        )
    def __exit__(self, *_args: object) -> None:
        for descriptor in self.fds:
            os.close(descriptor)
def _file_identity(info: os.stat_result) -> FileIdentity:
    return FileIdentity(info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode))
