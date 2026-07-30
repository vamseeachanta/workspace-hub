"""Immutable, replacement-free snapshots of committed template objects."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
from typing import Iterator
import unicodedata

from .bootstrap_git import isolated_env, trusted_executable


class BootstrapSnapshotError(RuntimeError):
    """Committed template objects violate the closed snapshot contract."""


@dataclass(frozen=True, slots=True)
class TemplateMember:
    path: str
    data: bytes | None
    mode: int
    object_oid: str

    @property
    def is_directory(self) -> bool:
        return self.data is None


@dataclass(frozen=True, slots=True)
class TemplateSnapshot:
    commit_oid: str
    tree_oid: str
    members: tuple[TemplateMember, ...]


@dataclass(frozen=True, slots=True)
class _BoundTemplate:
    worktree_fd: int
    git_fd: int


@dataclass(slots=True)
class _Budget:
    commands: int = 0
    members: int = 0
    path_bytes: int = 0
    tree_bytes: int = 0
    blob_bytes: int = 0


_OID = re.compile(rb"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_TREE_OUTPUT_LIMIT = 4 * 1024 * 1024
_AGGREGATE_TREE_LIMIT = 8 * 1024 * 1024
_BLOB_LIMIT = 16 * 1024 * 1024
_TOTAL_BLOB_LIMIT = 64 * 1024 * 1024
_PATH_BYTES_LIMIT = 1024 * 1024
_MEMBER_LIMIT = 8192
_DEPTH_LIMIT = 32
_COMMAND_LIMIT = 16384
_GIT_TIMEOUT = 5
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def _read_bounded(stream, limit: int, label: str) -> bytes:
    size = os.fstat(stream.fileno()).st_size
    if size > limit:
        raise BootstrapSnapshotError(f"Git {label} output exceeds size limit")
    stream.seek(0)
    return stream.read(limit + 1)


def _execute(command: list[str], pass_fds: tuple[int, ...], limit: int) -> bytes:
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            result = subprocess.run(
                command, check=False, stdout=stdout, stderr=stderr,
                pass_fds=pass_fds, env=isolated_env(), timeout=_GIT_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            raise BootstrapSnapshotError("Git snapshot command timed out") from exc
        error = _read_bounded(stderr, _TREE_OUTPUT_LIMIT, "error")
        if result.returncode != 0:
            detail = error.decode("utf-8", errors="replace").strip()
            raise BootstrapSnapshotError(f"Git snapshot command failed: {detail}")
        return _read_bounded(stdout, limit, "snapshot")


def _initial_git(
    worktree_fd: int, budget: _Budget, *args: str, limit: int = 4096,
) -> bytes:
    budget.commands += 1
    if budget.commands > _COMMAND_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds command limit")
    command = [trusted_executable("git"), "-C", f"/proc/self/fd/{worktree_fd}", *args]
    return _execute(command, (worktree_fd,), limit)


def _run_git(
    bound: _BoundTemplate, args: tuple[str, ...], limit: int, budget: _Budget,
) -> bytes:
    budget.commands += 1
    if budget.commands > _COMMAND_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds command limit")
    command = [
        trusted_executable("git"), f"--git-dir=/proc/self/fd/{bound.git_fd}",
        f"--work-tree=/proc/self/fd/{bound.worktree_fd}", *args,
    ]
    return _execute(command, (bound.git_fd, bound.worktree_fd), limit)


def _open_gitdir(worktree_fd: int, budget: _Budget) -> int:
    raw = _initial_git(worktree_fd, budget, "rev-parse", "--absolute-git-dir")
    try:
        gitdir = Path(raw.rstrip(b"\n").decode("utf-8"))
    except UnicodeError as exc:
        raise BootstrapSnapshotError("Git directory path is not UTF-8") from exc
    if not gitdir.is_absolute() or b"\0" in raw:
        raise BootstrapSnapshotError("Git directory path is invalid")
    before = os.stat(gitdir, follow_symlinks=False)
    if not stat.S_ISDIR(before.st_mode):
        raise BootstrapSnapshotError("resolved Git directory is not a directory")
    descriptor = os.open(gitdir, _DIR_FLAGS)
    if (before.st_dev, before.st_ino) != (
        os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino,
    ):
        os.close(descriptor)
        raise BootstrapSnapshotError("Git directory changed while binding")
    return descriptor


@contextmanager
def _bind_template(path: Path, budget: _Budget) -> Iterator[_BoundTemplate]:
    worktree_fd = git_fd = -1
    try:
        worktree_fd = os.open(Path(path), _DIR_FLAGS)
        git_fd = _open_gitdir(worktree_fd, budget)
        yield _BoundTemplate(worktree_fd, git_fd)
    except OSError as exc:
        raise BootstrapSnapshotError(f"template repository bind failed: {exc}") from exc
    finally:
        for descriptor in (git_fd, worktree_fd):
            if descriptor >= 0:
                os.close(descriptor)


def _object_id(raw: bytes, label: str) -> str:
    value = raw.rstrip(b"\n")
    if not _OID.fullmatch(value):
        raise BootstrapSnapshotError(f"Git returned invalid {label} object ID")
    return value.decode("ascii")


def _safe_name(raw: bytes) -> str:
    try:
        name = raw.decode("utf-8")
    except UnicodeError as exc:
        raise BootstrapSnapshotError("template tree contains a non-UTF-8 path") from exc
    unsafe = any(unicodedata.category(character) == "Cc" for character in name)
    path = PurePosixPath(name)
    if unsafe or not name or name in {".", "..", ".git"}:
        raise BootstrapSnapshotError(f"unsafe template path component: {name!r}")
    if "/" in name or "\\" in name or str(path) != name:
        raise BootstrapSnapshotError(f"invalid template path component: {name!r}")
    return name


def _decode_header(raw: bytes, label: str) -> str:
    try:
        return raw.decode("ascii")
    except UnicodeError as exc:
        raise BootstrapSnapshotError(f"Git tree contains invalid {label}") from exc


def _tree_entries(
    bound: _BoundTemplate, tree_oid: str, budget: _Budget,
) -> tuple[tuple[str, str, str, str], ...]:
    raw = _run_git(bound, ("ls-tree", "-z", tree_oid), _TREE_OUTPUT_LIMIT, budget)
    budget.tree_bytes += len(raw)
    if budget.tree_bytes > _AGGREGATE_TREE_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds tree-output limit")
    if not raw or not raw.endswith(b"\0") or b"\0\0" in raw:
        raise BootstrapSnapshotError("malformed NUL framing in Git tree output")
    entries: list[tuple[str, str, str, str]] = []
    names: set[str] = set()
    for record in raw[:-1].split(b"\0"):
        try:
            header, raw_name = record.split(b"\t", 1)
            mode, kind, raw_oid = header.split(b" ", 2)
        except ValueError as exc:
            raise BootstrapSnapshotError("malformed Git tree record") from exc
        name = _safe_name(raw_name)
        if name in names:
            raise BootstrapSnapshotError(f"duplicate template tree entry: {name}")
        names.add(name)
        entries.append((_decode_header(mode, "mode"), _decode_header(kind, "type"), _object_id(raw_oid, "tree entry"), name))
    return tuple(entries)


def _claim_member(path: str, depth: int, budget: _Budget) -> None:
    if depth > _DEPTH_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds depth limit")
    budget.members += 1
    budget.path_bytes += len(path.encode("utf-8"))
    if budget.members > _MEMBER_LIMIT or budget.path_bytes > _PATH_BYTES_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds member/path limit")


def _read_blob(
    bound: _BoundTemplate, oid: str, budget: _Budget, cache: dict[str, bytes],
) -> bytes:
    cached = cache.get(oid)
    if cached is not None:
        size = len(cached)
    else:
        raw = _run_git(bound, ("cat-file", "-s", oid), 64, budget).rstrip(b"\n")
        if not raw.isdigit() or int(raw) > _BLOB_LIMIT:
            raise BootstrapSnapshotError("template blob has invalid or excessive size")
        size = int(raw)
    if budget.blob_bytes + size > _TOTAL_BLOB_LIMIT:
        raise BootstrapSnapshotError("template snapshot exceeds total size limit")
    budget.blob_bytes += size
    if cached is not None:
        return cached
    data = _run_git(bound, ("cat-file", "blob", oid), size, budget)
    if len(data) != size:
        raise BootstrapSnapshotError("template blob size changed while reading")
    cache[oid] = data
    return data


def _walk_tree(
    bound: _BoundTemplate, tree_oid: str, budget: _Budget,
) -> tuple[TemplateMember, ...]:
    members: list[TemplateMember] = []
    cache: dict[str, bytes] = {}

    def walk(current_oid: str, prefix: str = "", depth: int = 0) -> None:
        if depth > _DEPTH_LIMIT:
            raise BootstrapSnapshotError("template snapshot exceeds depth limit")
        for mode, kind, oid, name in _tree_entries(bound, current_oid, budget):
            path = f"{prefix}/{name}" if prefix else name
            _claim_member(path, depth, budget)
            if (mode, kind) == ("040000", "tree"):
                members.append(TemplateMember(path, None, 0o755, oid))
                walk(oid, path, depth + 1)
            elif kind == "blob" and mode in {"100644", "100755"}:
                data = _read_blob(bound, oid, budget, cache)
                members.append(TemplateMember(path, data, int(mode[-3:], 8), oid))
            else:
                raise BootstrapSnapshotError(f"unsupported Git entry mode/type: {mode} {kind}")

    walk(tree_oid)
    return tuple(members)


def load_committed_snapshot(template_worktree: Path) -> TemplateSnapshot:
    """Bind repository authority and return exact committed template objects."""
    budget = _Budget()
    with _bind_template(Path(template_worktree), budget) as bound:
        commit = _object_id(
            _run_git(bound, ("rev-parse", "HEAD^{commit}"), 128, budget), "commit",
        )
        tree = _object_id(
            _run_git(bound, ("rev-parse", f"{commit}:templates/client-llm-wiki"), 128, budget),
            "template tree",
        )
        members = _walk_tree(bound, tree, budget)
        if not members:
            raise BootstrapSnapshotError("committed template is empty")
        return TemplateSnapshot(commit, tree, members)
