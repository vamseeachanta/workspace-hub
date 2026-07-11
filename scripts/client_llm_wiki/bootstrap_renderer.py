"""Pinned Git-object renderer with descriptor-relative installation."""

from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
from typing import Callable, Iterator, Mapping

from .bootstrap_snapshot import (
    BootstrapSnapshotError,
    TemplateMember as _TemplateMember,
    load_committed_snapshot,
)


class BootstrapRenderError(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class FileIdentity:
    device: int
    inode: int
    file_type: int

@dataclass(slots=True)
class BoundClone:
    display_path: Path
    basename: str
    parent_fd: int
    root_fd: int
    git_fd: int
    root_id: FileIdentity
    git_id: FileIdentity

@dataclass(frozen=True, slots=True)
class RenderTokens:
    short_name: str
    short_name_upper: str
    repo_slug: str
    raw_source_status: str
    ingestion_enabled: bool

@dataclass(frozen=True, slots=True)
class RenderManifest:
    template_commit: str
    clone_device: int
    clone_inode: int
    created_paths: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class _CreatedArtifact:
    relative_path: str
    parent_fd: int
    name: str
    identity: FileIdentity
    is_directory: bool

Failpoint = Callable[[str, str | None, int | None], None]
FinalValidator = Callable[[BoundClone], None]
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def _no_failpoint(_event: str, _path: str | None, _fd: int | None) -> None:
    pass

def _identity(info: os.stat_result) -> FileIdentity:
    return FileIdentity(info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode))


def _same_identity(info: os.stat_result, expected: FileIdentity) -> bool:
    return _identity(info) == expected


def _open_bound_directory(parent_fd: int, name: str) -> tuple[int, FileIdentity]:
    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if stat.S_ISLNK(before.st_mode):
        raise BootstrapRenderError(f"symlink rejected by no-follow bind: {name}")
    if not stat.S_ISDIR(before.st_mode):
        raise BootstrapRenderError(f"not a directory: {name}")
    descriptor = os.open(name, _DIR_FLAGS, dir_fd=parent_fd)
    identity = _identity(os.fstat(descriptor))
    if identity != _identity(before):
        os.close(descriptor)
        raise BootstrapRenderError(f"directory identity changed while binding: {name}")
    return descriptor, identity


@contextmanager
def bind_empty_clone(target: Path) -> Iterator[BoundClone]:
    target = Path(target)
    parent_fd = root_fd = git_fd = -1
    try:
        parent_fd = os.open(target.parent, _DIR_FLAGS)
        root_fd, root_id = _open_bound_directory(parent_fd, target.name)
        if os.listdir(root_fd) != [".git"]:
            raise BootstrapRenderError("clone must contain only a real .git directory")
        git_fd, git_id = _open_bound_directory(root_fd, ".git")
        yield BoundClone(target, target.name, parent_fd, root_fd, git_fd, root_id, git_id)
    except (BootstrapRenderError, OSError) as exc:
        if isinstance(exc, BootstrapRenderError):
            raise
        raise BootstrapRenderError(f"clone bind failed (no-follow): {exc}") from exc
    finally:
        for descriptor in (git_fd, root_fd, parent_fd):
            if descriptor >= 0:
                os.close(descriptor)


def _render_member(member: _TemplateMember, tokens: RenderTokens) -> _TemplateMember:
    if member.is_directory:
        return member
    try:
        text = member.data.decode("utf-8")
    except UnicodeError as exc:
        raise BootstrapRenderError(f"template file is not UTF-8: {member.path}") from exc
    replacements = {
        "<CLIENT_SHORT_NAME>": tokens.short_name,
        "<CLIENT_SHORT_NAME_UPPER>": tokens.short_name_upper,
        "<CLIENT_PRIVATE_REPO>": tokens.repo_slug,
        "<RAW_SOURCE_STATUS>": tokens.raw_source_status,
        "<INGESTION_ENABLED>": str(tokens.ingestion_enabled).lower(),
    }
    for placeholder, replacement in replacements.items():
        text = text.replace(placeholder, replacement)
    unresolved = re.search(r"<CLIENT_[A-Z0-9_]+>", text)
    if unresolved or "<RAW_SOURCE_STATUS>" in text or "<INGESTION_ENABLED>" in text:
        token = unresolved.group(0) if unresolved else "raw-state placeholder"
        raise BootstrapRenderError(f"unresolved placeholder {token} in {member.path}")
    return _TemplateMember(
        member.path, text.encode("utf-8"), member.mode, member.object_oid,
    )


def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        offset += os.write(descriptor, data[offset:])


def _create_directories(root_fd: int, members: tuple[_TemplateMember, ...], ledger: list[_CreatedArtifact], directory_fds: dict[str, int], event: str, failpoint: Failpoint) -> None:
    paths = sorted((member.path for member in members if member.is_directory), key=lambda path: (path.count("/"), path))
    for relative in paths:
        parent, name = str(PurePosixPath(relative).parent), PurePosixPath(relative).name
        parent = "" if parent == "." else parent
        parent_fd = directory_fds[parent]
        os.mkdir(name, 0o755, dir_fd=parent_fd)
        descriptor, identity = _open_bound_directory(parent_fd, name)
        directory_fds[relative] = descriptor
        ledger.append(_CreatedArtifact(relative, parent_fd, name, identity, True))
        os.fchmod(descriptor, 0o755)
        failpoint(event, relative, descriptor)


def _create_files(members: tuple[_TemplateMember, ...], ledger: list[_CreatedArtifact], directory_fds: Mapping[str, int], event: str, failpoint: Failpoint) -> None:
    for member in sorted(members, key=lambda item: item.path):
        if member.is_directory:
            continue
        path = PurePosixPath(member.path)
        parent = "" if str(path.parent) == "." else str(path.parent)
        parent_fd = directory_fds[parent]
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        descriptor = os.open(path.name, flags, member.mode, dir_fd=parent_fd)
        try:
            identity = _identity(os.fstat(descriptor))
            ledger.append(_CreatedArtifact(member.path, parent_fd, path.name, identity, False))
            _write_all(descriptor, member.data)
            os.fchmod(descriptor, member.mode)
            failpoint(event, member.path, descriptor)
        finally:
            os.close(descriptor)


def _materialize(root_fd: int, members: tuple[_TemplateMember, ...], event: str, failpoint: Failpoint) -> tuple[list[_CreatedArtifact], list[int]]:
    ledger: list[_CreatedArtifact] = []
    directory_fds = {"": root_fd}
    try:
        _create_directories(root_fd, members, ledger, directory_fds, event, failpoint)
        _create_files(members, ledger, directory_fds, event, failpoint)
        return ledger, [fd for path, fd in directory_fds.items() if path]
    except Exception:
        _cleanup_created(ledger, failpoint)
        for path, descriptor in reversed(tuple(directory_fds.items())):
            if path:
                os.close(descriptor)
        raise


def _cleanup_created(ledger: list[_CreatedArtifact], failpoint: Failpoint) -> bool:
    complete = True
    for artifact in reversed(ledger):
        try:
            failpoint("before_cleanup_member", artifact.relative_path, artifact.parent_fd)
            current = os.stat(artifact.name, dir_fd=artifact.parent_fd, follow_symlinks=False)
            if not _same_identity(current, artifact.identity):
                complete = False
                continue
            if artifact.is_directory:
                os.rmdir(artifact.name, dir_fd=artifact.parent_fd)
            else:
                os.unlink(artifact.name, dir_fd=artifact.parent_fd)
        except OSError:
            complete = False
            continue
    return complete


@contextmanager
def _bound_stage(clone: BoundClone, failpoint: Failpoint) -> Iterator[int]:
    stage_path = tempfile.mkdtemp(prefix=".client-wiki-stage-", dir=f"/proc/self/fd/{clone.parent_fd}")
    stage_name = Path(stage_path).name
    stage_fd, stage_id = _open_bound_directory(clone.parent_fd, stage_name)
    body_failed = False
    try:
        failpoint("stage_bound", stage_name, stage_fd)
        yield stage_fd
    except BaseException:
        body_failed = True
        raise
    finally:
        os.close(stage_fd)
        removed = False
        try:
            current = os.stat(stage_name, dir_fd=clone.parent_fd, follow_symlinks=False)
            if _same_identity(current, stage_id):
                os.rmdir(stage_name, dir_fd=clone.parent_fd)
                removed = True
        except OSError:
            pass
        if not removed and not body_failed:
            raise BootstrapRenderError("stage cleanup incomplete")


def _revalidate_clone(clone: BoundClone, ledger: list[_CreatedArtifact], directory_fds: list[int]) -> None:
    path_info = os.stat(clone.basename, dir_fd=clone.parent_fd, follow_symlinks=False)
    git_info = os.stat(".git", dir_fd=clone.root_fd, follow_symlinks=False)
    if not _same_identity(path_info, clone.root_id):
        raise BootstrapRenderError("clone path identity changed")
    if not _same_identity(os.fstat(clone.root_fd), clone.root_id):
        raise BootstrapRenderError("bound clone identity changed")
    if not _same_identity(git_info, clone.git_id) or not _same_identity(os.fstat(clone.git_fd), clone.git_id):
        raise BootstrapRenderError(".git identity changed")
    expected: dict[int, set[str]] = {clone.root_fd: {".git"}}
    for artifact in ledger:
        expected.setdefault(artifact.parent_fd, set()).add(artifact.name)
        current = os.stat(artifact.name, dir_fd=artifact.parent_fd, follow_symlinks=False)
        if not _same_identity(current, artifact.identity):
            raise BootstrapRenderError("rendered inventory identity changed")
    for descriptor in directory_fds:
        expected.setdefault(descriptor, set())
    if any(set(os.listdir(fd)) != names for fd, names in expected.items()):
        raise BootstrapRenderError("rendered inventory contains unexpected members")


def render_committed_template(
    clone: BoundClone, template_worktree: Path, tokens: RenderTokens, *, _failpoint: Failpoint | None = None, _final_validator: FinalValidator | None = None
) -> RenderManifest:
    failpoint = _failpoint or _no_failpoint
    ledger: list[_CreatedArtifact] = []
    target_fds: list[int] = []
    try:
        failpoint("clone_bound", None, clone.root_fd)
        snapshot = load_committed_snapshot(Path(template_worktree))
        members = {member.path: member for member in snapshot.members}
        firewall = (members.get(".gitignore"), members.get(".claude/CLAUDE.md"))
        if any(member is None or member.data is None or member.mode != 0o644 for member in firewall):
            raise BootstrapRenderError("committed template has an invalid privacy firewall")
        rendered = tuple(_render_member(member, tokens) for member in snapshot.members)
        with _bound_stage(clone, failpoint) as stage_fd:
            stage_ledger, stage_fds = _materialize(stage_fd, rendered, "stage_member_bound", failpoint)
            stage_clean = _cleanup_created(stage_ledger, failpoint)
            for descriptor in reversed(stage_fds):
                os.close(descriptor)
            if not stage_clean:
                raise BootstrapRenderError("stage cleanup incomplete")
        ledger, target_fds = _materialize(clone.root_fd, rendered, "target_member_bound", failpoint)
        failpoint("before_final_revalidation", None, clone.root_fd)
        _revalidate_clone(clone, ledger, target_fds)
        if _final_validator is not None:
            _final_validator(clone)
        return RenderManifest(snapshot.commit_oid, clone.root_id.device, clone.root_id.inode, tuple(artifact.relative_path for artifact in ledger))
    except Exception as exc:
        _cleanup_created(ledger, failpoint)
        if isinstance(exc, BootstrapRenderError):
            raise
        if isinstance(exc, BootstrapSnapshotError):
            raise BootstrapRenderError(str(exc)) from exc
        raise BootstrapRenderError(str(exc)) from exc
    finally:
        for descriptor in reversed(target_fds):
            os.close(descriptor)
