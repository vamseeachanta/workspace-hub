"""Pinned Git-object renderer with descriptor-relative installation."""

from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass, field
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Iterator, Mapping

from .bootstrap_snapshot import (
    BootstrapSnapshotError,
    TemplateMember as _TemplateMember,
    load_committed_snapshot,
)


@dataclass(frozen=True, slots=True)
class RenderResidue:
    template_commit: str
    clone_device: int
    clone_inode: int
    completed_members: tuple[str, ...]
    uncertain_member: str | None
    failure_stage: str
    residue_policy: str = "preserved"
    instruction: str = "Do not retry this clone; inspect and dispose of residue manually."


class BootstrapRenderError(RuntimeError):
    def __init__(self, message: str, *, residue: RenderResidue | None = None):
        super().__init__(message)
        self.residue = residue

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


@dataclass(slots=True)
class _RenderProgress:
    current: str | None = None
    stage: str = "snapshot_or_validation"
    completed: list[str] = field(default_factory=list)

_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_RESIDUE_MEMBER_LIMIT = 8192


_FAILPOINTS = {"create", "bind", "record", "write", "chmod", "final_validation"}


def _set_stage(progress: _RenderProgress, stage: str) -> None:
    progress.stage = stage


def _inject(selected: str | None, stage: str) -> None:
    if selected == stage:
        raise RuntimeError(f"injected {stage} failure")


def _record_artifact(ledger: list[_CreatedArtifact], artifact: _CreatedArtifact) -> None:
    ledger.append(artifact)

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
    try:
        identity = _identity(os.fstat(descriptor))
        if identity != _identity(before):
            raise BootstrapRenderError(f"directory identity changed while binding: {name}")
        return descriptor, identity
    except BaseException:
        os.close(descriptor)
        raise


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


def _create_directories(root_fd: int, members: tuple[_TemplateMember, ...], ledger: list[_CreatedArtifact], directory_fds: dict[str, int], failpoint: str | None, progress: _RenderProgress) -> None:
    paths = sorted((member.path for member in members if member.is_directory), key=lambda path: (path.count("/"), path))
    for relative in paths:
        parent, name = str(PurePosixPath(relative).parent), PurePosixPath(relative).name
        parent = "" if parent == "." else parent
        parent_fd = directory_fds[parent]
        progress.current = relative
        _set_stage(progress, "create")
        os.mkdir(name, 0o755, dir_fd=parent_fd)
        _inject(failpoint, "create")
        _set_stage(progress, "bind")
        descriptor, identity = _open_bound_directory(parent_fd, name)
        try:
            _inject(failpoint, "bind")
            directory_fds[relative] = descriptor
            _set_stage(progress, "record")
            _record_artifact(ledger, _CreatedArtifact(relative, parent_fd, name, identity, True))
            _inject(failpoint, "record")
            _set_stage(progress, "chmod")
            os.fchmod(descriptor, 0o755)
            _inject(failpoint, "chmod")
            progress.completed.append(relative)
        except BaseException:
            if relative not in directory_fds:
                os.close(descriptor)
            raise


def _create_files(members: tuple[_TemplateMember, ...], ledger: list[_CreatedArtifact], directory_fds: Mapping[str, int], failpoint: str | None, progress: _RenderProgress) -> None:
    for member in sorted(members, key=lambda item: item.path):
        if member.is_directory:
            continue
        path = PurePosixPath(member.path)
        parent = "" if str(path.parent) == "." else str(path.parent)
        parent_fd = directory_fds[parent]
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        progress.current = member.path
        _set_stage(progress, "create")
        descriptor = os.open(path.name, flags, member.mode, dir_fd=parent_fd)
        try:
            _inject(failpoint, "create")
            _set_stage(progress, "bind")
            identity = _identity(os.fstat(descriptor))
            _inject(failpoint, "bind")
            _set_stage(progress, "record")
            _record_artifact(ledger, _CreatedArtifact(member.path, parent_fd, path.name, identity, False))
            _inject(failpoint, "record")
            _set_stage(progress, "write")
            _write_all(descriptor, member.data)
            _inject(failpoint, "write")
            _set_stage(progress, "chmod")
            os.fchmod(descriptor, member.mode)
            _inject(failpoint, "chmod")
            progress.completed.append(member.path)
        finally:
            os.close(descriptor)


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


def _render_committed_template(
    clone: BoundClone, template_worktree: Path, tokens: RenderTokens, failpoint: str | None,
) -> RenderManifest:
    if failpoint is not None and failpoint not in _FAILPOINTS:
        raise TypeError("_failpoint must be an internal named failpoint")
    ledger: list[_CreatedArtifact] = []
    directory_fds = {"": clone.root_fd}
    progress = _RenderProgress()
    try:
        snapshot = load_committed_snapshot(Path(template_worktree))
        members = {member.path: member for member in snapshot.members}
        firewall = (members.get(".gitignore"), members.get(".claude/CLAUDE.md"))
        if any(member is None or member.data is None or member.mode != 0o644 for member in firewall):
            raise BootstrapRenderError("committed template has an invalid privacy firewall")
        rendered = tuple(_render_member(member, tokens) for member in snapshot.members)
        if len(rendered) > _RESIDUE_MEMBER_LIMIT:
            raise BootstrapRenderError("template exceeds residue member limit")
        _create_directories(clone.root_fd, rendered, ledger, directory_fds, failpoint, progress)
        _create_files(rendered, ledger, directory_fds, failpoint, progress)
        progress.current = None
        _set_stage(progress, "final_validation")
        _inject(failpoint, "final_validation")
        _revalidate_clone(clone, ledger, [fd for path, fd in directory_fds.items() if path])
        return RenderManifest(snapshot.commit_oid, clone.root_id.device, clone.root_id.inode, tuple(artifact.relative_path for artifact in ledger))
    except BaseException as exc:
        if "snapshot" not in locals() or progress.stage == "snapshot_or_validation":
            if isinstance(exc, BootstrapRenderError):
                raise
            if isinstance(exc, BootstrapSnapshotError):
                raise BootstrapRenderError(str(exc)) from exc
            raise BootstrapRenderError("template validation failed") from exc
        residue = RenderResidue(
            snapshot.commit_oid, clone.root_id.device, clone.root_id.inode,
            tuple(progress.completed), progress.current, progress.stage,
        )
        message = f"render failed at {progress.stage} ({type(exc).__name__})"
        raise BootstrapRenderError(message, residue=residue) from exc
    finally:
        for path, descriptor in reversed(tuple(directory_fds.items())):
            if not path:
                continue
            os.close(descriptor)


def render_committed_template(
    clone: BoundClone, template_worktree: Path, tokens: RenderTokens,
) -> RenderManifest:
    return _render_committed_template(clone, template_worktree, tokens, None)


def _render_committed_template_for_test(
    clone: BoundClone, template_worktree: Path, tokens: RenderTokens, *, failpoint: str,
) -> RenderManifest:
    return _render_committed_template(clone, template_worktree, tokens, failpoint)
