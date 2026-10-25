"""Descriptor-bound normalization of a newly cloned empty repository."""

from __future__ import annotations

import os
import re
import stat
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .bootstrap_git import (
    BootstrapGitError,
    isolated_env,
    trusted_executable,
    validate_clone_config,
    validate_clone_config_for_head_binding,
)
from .bootstrap_layout import BoundCloneLayout
from .bootstrap_renderer import BoundClone, bind_empty_clone


def _run(clone: BoundClone, *args: str) -> subprocess.CompletedProcess[str]:
    # Git opens local config even for read-only plumbing. Give it a private
    # view with no local config, while retaining the bound repository state.
    with tempfile.TemporaryDirectory(prefix="git-preflight-") as scratch:
        view = Path(scratch)
        names = os.listdir(clone.git_fd)
        if "commondir" in names:
            raise BootstrapGitError("new clone must have a standalone Git directory")
        for name in names:
            if name not in {"config", "HEAD"}:
                (view / name).symlink_to(f"/proc/self/fd/{clone.git_fd}/{name}")
        head_fd = os.open(
            "HEAD", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
            dir_fd=clone.git_fd,
        )
        try:
            if not stat.S_ISREG(os.fstat(head_fd).st_mode):
                raise BootstrapGitError("clone HEAD is not a regular file")
            # A valid ref must fit the filesystem's path representation.
            limit = os.fpathconf(clone.git_fd, "PC_PATH_MAX")
            payload = os.read(head_fd, limit + 1)
            if len(payload) > limit:
                raise BootstrapGitError("clone HEAD exceeds the filesystem path limit")
            (view / "HEAD").write_bytes(payload)
        finally:
            os.close(head_fd)
        try:
            return subprocess.run(
                [
                    trusted_executable("git"), f"--git-dir={view.as_posix()}",
                    f"--work-tree=/proc/self/fd/{clone.root_fd}", *args,
                ],
                check=False, capture_output=True, text=True, encoding="utf-8",
                pass_fds=(clone.root_fd, clone.git_fd), env=isolated_env(), timeout=5,
            )
        except subprocess.TimeoutExpired as exc:
            raise BootstrapGitError("new clone Git operation timed out") from exc


def _require(clone: BoundClone, *args: str) -> str:
    result = _run(clone, *args)
    if result.returncode != 0:
        raise BootstrapGitError("new clone Git operation failed")
    return result.stdout.strip()


def _canonical_config(parsed: dict[str, str]) -> bytes:
    core = ("repositoryformatversion", "filemode", "bare", "logallrefupdates")
    remote = ("url", "pushurl", "fetch")
    lines = ["[core]"]
    lines.extend(
        f"\t{name} = {parsed[f'core.{name}']}" for name in core
        if f"core.{name}" in parsed
    )
    lines.append('[remote "origin"]')
    lines.extend(
        f"\t{name} = {parsed[f'remote.origin.{name}']}" for name in remote
        if f"remote.origin.{name}" in parsed
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _rewrite_config(config_fd: int, parsed: dict[str, str]) -> None:
    payload = _canonical_config(parsed)
    os.lseek(config_fd, 0, os.SEEK_SET)
    os.ftruncate(config_fd, 0)
    offset = 0
    while offset < len(payload):
        offset += os.write(config_fd, payload[offset:])
    os.fsync(config_fd)


def _bound_layout(clone: BoundClone, config_fd: int) -> BoundCloneLayout:
    return BoundCloneLayout(clone.parent_fd, clone.root_fd, clone.git_fd, config_fd)


def _check_config_identity(clone: BoundClone, expected: tuple[int, int]) -> None:
    info = os.stat("config", dir_fd=clone.git_fd, follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or (info.st_dev, info.st_ino) != expected:
        raise BootstrapGitError("clone config identity changed")


def _authorize_and_normalize(clone: BoundClone, repo_slug: str) -> tuple[int, int]:
    config_fd = os.open(
        # POSIX.1-2024 open(), O_NONBLOCK: reject special files before parsing.
        "config", os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
        dir_fd=clone.git_fd,
    )
    try:
        if not stat.S_ISREG(os.fstat(config_fd).st_mode):
            raise BootstrapGitError("held clone config is not a regular file")
        head = _require(clone, "symbolic-ref", "-q", "HEAD")
        if re.fullmatch(r"refs/heads/[A-Za-z0-9._-]+", head) is None:
            raise BootstrapGitError("new clone HEAD is not an unborn branch")
        if _run(clone, "show-ref", "--verify", "--quiet", head).returncode != 1:
            raise BootstrapGitError("new clone HEAD must be truly unborn")
        if _require(clone, "status", "--porcelain=v1", "--untracked-files=all"):
            raise BootstrapGitError("new clone must be clean and empty")
        parsed = validate_clone_config_for_head_binding(
            _bound_layout(clone, config_fd), repo_slug, head,
        )
        info = os.fstat(config_fd)
        identity = (info.st_dev, info.st_ino)
        _check_config_identity(clone, identity)
        _rewrite_config(config_fd, parsed)
        _check_config_identity(clone, identity)
        return identity
    finally:
        os.close(config_fd)


def _strict_verify(
    clone: BoundClone, repo_slug: str, config_identity: tuple[int, int] | None = None,
) -> None:
    info = os.stat(".git", dir_fd=clone.root_fd, follow_symlinks=False)
    expected = (clone.git_id.device, clone.git_id.inode, clone.git_id.file_type)
    if (info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)) != expected:
        raise BootstrapGitError("new clone Git directory identity changed")
    config_fd = os.open(
        "config", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
        dir_fd=clone.git_fd,
    )
    try:
        if config_identity is not None:
            info = os.fstat(config_fd)
            if (info.st_dev, info.st_ino) != config_identity:
                raise BootstrapGitError("clone config identity changed")
        validate_clone_config(_bound_layout(clone, config_fd), repo_slug)
        if _require(clone, "symbolic-ref", "-q", "HEAD") != "refs/heads/main":
            raise BootstrapGitError("clone HEAD must be the symbolic main branch")
        if _run(clone, "show-ref", "--verify", "--quiet", "refs/heads/main").returncode != 1:
            raise BootstrapGitError("clone HEAD main branch must be truly unborn")
    finally:
        os.close(config_fd)


@contextmanager
def _main_head_lock(clone: BoundClone):
    try:
        lock_fd = os.open(
            "HEAD.lock", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
            0o666, dir_fd=clone.git_fd,
        )
    except OSError as exc:
        raise BootstrapGitError("clone HEAD lock cannot be created") from exc
    identity = os.fstat(lock_fd)
    try:
        yield lock_fd
    except OSError as exc:
        raise BootstrapGitError("clone HEAD update failed") from exc
    finally:
        os.close(lock_fd)
        try:
            current = os.stat("HEAD.lock", dir_fd=clone.git_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass  # Successful publication consumes this call's lock.
        else:
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                os.unlink("HEAD.lock", dir_fd=clone.git_fd)


def bind_clone_to_main(target: Path, repo_slug: str) -> None:
    """Normalize an authorized empty clone and strictly verify exact main."""
    with bind_empty_clone(target) as clone, _main_head_lock(clone) as head_fd:
        config_identity = _authorize_and_normalize(clone, repo_slug)
        payload = b"ref: refs/heads/main\n"
        while payload:
            payload = payload[os.write(head_fd, payload):]
        os.fsync(head_fd)
        _check_config_identity(clone, config_identity)
        os.rename("HEAD.lock", "HEAD", src_dir_fd=clone.git_fd, dst_dir_fd=clone.git_fd)
        _strict_verify(clone, repo_slug, config_identity)
