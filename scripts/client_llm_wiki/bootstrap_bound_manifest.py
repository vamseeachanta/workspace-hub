"""Retained-descriptor manifest validation for scaffold finalization."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json
import hashlib
import os
from pathlib import Path
import stat
import re
from typing import Iterator

from . import bootstrap_attestation as attestation
from .bootstrap_git import validate_clone_config
from .bootstrap_layout import BoundCloneLayout


class BoundManifestError(RuntimeError):
    """Retained manifest evidence no longer matches trusted state."""


@dataclass(frozen=True, slots=True)
class BoundValidationContext:
    clone: BoundCloneLayout
    manifest_parent_fd: int
    manifest_fd: int
    backing_fd: int
    claims: dict
    manifest_bytes: bytes
    repo: str
    template_commit: str
    template_tree: str
    expected_files: dict[str, dict]
    parsed_config: dict[str, str]


_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
_LIMIT = 8 * 1024 * 1024


def _read(fd: int) -> bytes:
    before = os.fstat(fd)
    if not stat.S_ISREG(before.st_mode) or stat.S_IMODE(before.st_mode) != 0o600:
        raise BoundManifestError("manifest descriptor is unsafe")
    size, _digest, data = attestation.stable_digest(fd, before, _LIMIT)
    if size != before.st_size:
        raise BoundManifestError("manifest descriptor changed")
    return data


def _strict_claims(data: bytes) -> dict:
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise BoundManifestError("duplicate manifest key")
            value[key] = item
        return value
    try:
        claims = json.loads(data, object_pairs_hook=pairs)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise BoundManifestError("manifest is not strict JSON") from exc
    if not isinstance(claims, dict):
        raise BoundManifestError("manifest is not an object")
    return claims


@contextmanager
def bind_validation_context(
    clone: BoundCloneLayout, manifest: Path, repo: str,
    template_commit: str, template_tree: str, rendered_members=(),
) -> Iterator[BoundValidationContext]:
    """Bind manifest parent/final/backing once for all finalizer operations."""
    descriptors: list[int] = []
    try:
        parent = os.open(Path(manifest).absolute().parent, _DIR_FLAGS)
        descriptors.append(parent)
        final = os.open(Path(manifest).name, _FILE_FLAGS, dir_fd=parent)
        descriptors.append(final)
        data = _read(final)
        claims = _strict_claims(data)
        backing_name = claims.get("backing_name")
        final_name = Path(manifest).name
        pattern = rf"\.{re.escape(final_name)}\.backing-[1-9][0-9]*-[0-9a-f]{{16}}"
        if not isinstance(backing_name, str) or re.fullmatch(pattern, backing_name) is None:
            raise BoundManifestError("manifest backing name is invalid")
        backing = os.open(backing_name, _FILE_FLAGS, dir_fd=parent)
        descriptors.append(backing)
        expected_files = {
            member.path: {
                "type": "directory" if member.data is None else "file",
                "mode": member.mode, "size": 0 if member.data is None else len(member.data),
                "sha256": None if member.data is None else hashlib.sha256(member.data).hexdigest(),
            }
            for member in rendered_members
        }
        parsed_config = validate_clone_config(clone, repo)
        context = BoundValidationContext(
            clone, parent, final, backing, claims, data, repo,
            template_commit, template_tree, expected_files, parsed_config,
        )
        validate_bound_context(context)
        yield context
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _identity(info: os.stat_result) -> dict[str, int]:
    return {"device": info.st_dev, "inode": info.st_ino, "type": stat.S_IFMT(info.st_mode)}


def _identities(context: BoundValidationContext) -> dict[str, dict[str, int]]:
    clone = context.clone
    return {
        "parent": _identity(os.fstat(clone.parent_fd)),
        "root": _identity(os.fstat(clone.root_fd)),
        "git": _identity(os.fstat(clone.git_fd)),
        "config": _identity(os.fstat(clone.config_fd)),
        "manifest_parent": _identity(os.fstat(context.manifest_parent_fd)),
    }


def validate_bound_context(context: BoundValidationContext) -> None:
    """Independently validate only retained descriptors, never pathnames."""
    final_info = os.fstat(context.manifest_fd)
    backing_info = os.fstat(context.backing_fd)
    if (_identity(final_info) != _identity(backing_info)
            or final_info.st_nlink != 2 or backing_info.st_nlink != 2):
        raise BoundManifestError("manifest retained links differ")
    if _read(context.manifest_fd) != context.manifest_bytes:
        raise BoundManifestError("manifest final bytes changed")
    if _read(context.backing_fd) != context.manifest_bytes:
        raise BoundManifestError("manifest backing bytes changed")
    claims = context.claims
    if claims.get("registered_repo") != context.repo:
        raise BoundManifestError("manifest repository differs")
    if claims.get("template") != {
        "commit": context.template_commit, "tree": context.template_tree,
    }:
        raise BoundManifestError("manifest template differs")
    if claims.get("identities") != _identities(context):
        raise BoundManifestError("retained descriptor identities differ")
    config_info = os.fstat(context.clone.config_fd)
    size, digest, _data = attestation.stable_digest(
        context.clone.config_fd, config_info, _LIMIT,
    )
    config = claims.get("config", {})
    if (config.get("parsed") != context.parsed_config or config.get("size") != size
            or config.get("sha256") != digest):
        raise BoundManifestError("retained config differs")
    members, memberships = attestation.snapshot_clone(context.clone.root_fd)
    if claims.get("members") != members or claims.get("memberships") != memberships:
        raise BoundManifestError("independent scaffold reconstruction differs")
    if context.expected_files and members != context.expected_files:
        raise BoundManifestError("trusted rendered scaffold differs")
    expected_memberships: dict[str, list[str]] = {"": [".git"]}
    for path, record in context.expected_files.items():
        parent, _, name = path.rpartition("/")
        expected_memberships.setdefault(parent, []).append(name)
        if record["type"] == "directory":
            expected_memberships.setdefault(path, [])
    expected_memberships = {
        path: sorted(names) for path, names in expected_memberships.items()
    }
    if memberships != expected_memberships:
        raise BoundManifestError("trusted scaffold memberships differ")
