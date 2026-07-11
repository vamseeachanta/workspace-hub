"""Descriptor-bound clone layout primitives."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import stat
from typing import Iterator


@dataclass(frozen=True, slots=True)
class BoundCloneLayout:
    parent_fd: int
    root_fd: int
    git_fd: int
    config_fd: int


_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC


def _open_directory(name: str | Path, *, dir_fd: int | None = None) -> int:
    descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=dir_fd)
    if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise OSError("bound clone component is not a directory")
    return descriptor


@contextmanager
def bind_clone(target: Path) -> Iterator[BoundCloneLayout]:
    """Hold the clone root, Git directory, and exact config regular file."""
    descriptors: list[int] = []
    try:
        target = Path(target).absolute()
        parent_fd = _open_directory(target.parent)
        descriptors.append(parent_fd)
        root_fd = _open_directory(target.name, dir_fd=parent_fd)
        descriptors.append(root_fd)
        git_fd = _open_directory(".git", dir_fd=root_fd)
        descriptors.append(git_fd)
        config_fd = os.open("config", _FILE_FLAGS, dir_fd=git_fd)
        descriptors.append(config_fd)
        if not stat.S_ISREG(os.fstat(config_fd).st_mode):
            raise OSError("clone config is not a regular file")
        yield BoundCloneLayout(parent_fd, root_fd, git_fd, config_fd)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
