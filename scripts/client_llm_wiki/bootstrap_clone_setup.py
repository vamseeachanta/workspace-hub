"""Descriptor-bound normalization of a newly cloned empty repository."""

from __future__ import annotations

import os
import re
import stat
import subprocess
from pathlib import Path

from .bootstrap_git import (
    BootstrapGitError,
    isolated_env,
    trusted_executable,
    validate_clone_config_for_head_binding,
    validate_clone_git,
)
from .bootstrap_layout import BoundCloneLayout
from .bootstrap_renderer import BoundClone, bind_empty_clone


def _run(clone: BoundClone, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            trusted_executable("git"),
            f"--git-dir=/proc/self/fd/{clone.git_fd}",
            f"--work-tree=/proc/self/fd/{clone.root_fd}",
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
        pass_fds=(clone.root_fd, clone.git_fd),
        env=isolated_env(),
    )


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


def _authorize_and_normalize(clone: BoundClone, repo_slug: str) -> None:
    head = _require(clone, "symbolic-ref", "-q", "HEAD")
    if re.fullmatch(r"refs/heads/[A-Za-z0-9._-]+", head) is None:
        raise BootstrapGitError("new clone HEAD is not an unborn branch")
    if _run(clone, "rev-parse", "--verify", "HEAD").returncode == 0:
        raise BootstrapGitError("new clone HEAD must be unborn")
    if _require(clone, "status", "--porcelain=v1", "--untracked-files=all"):
        raise BootstrapGitError("new clone must be clean and empty")
    config_fd = os.open(
        "config", os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=clone.git_fd,
    )
    try:
        parsed = validate_clone_config_for_head_binding(
            _bound_layout(clone, config_fd), repo_slug, head,
        )
        _rewrite_config(config_fd, parsed)
    finally:
        os.close(config_fd)


def _strict_verify(clone: BoundClone, repo_slug: str) -> None:
    info = os.stat(".git", dir_fd=clone.root_fd, follow_symlinks=False)
    expected = (clone.git_id.device, clone.git_id.inode, clone.git_id.file_type)
    if (info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)) != expected:
        raise BootstrapGitError("new clone Git directory identity changed")
    config_fd = os.open(
        "config", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=clone.git_fd,
    )
    try:
        validate_clone_git(_bound_layout(clone, config_fd), repo_slug)
    finally:
        os.close(config_fd)


def bind_clone_to_main(target: Path, repo_slug: str) -> None:
    """Normalize an authorized empty clone and strictly verify exact main."""
    with bind_empty_clone(target) as clone:
        _authorize_and_normalize(clone, repo_slug)
        _require(clone, "symbolic-ref", "HEAD", "refs/heads/main")
        _strict_verify(clone, repo_slug)
