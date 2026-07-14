"""Retained-dirfd, isolated Git transport for authority audits."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


class GitTransportError(RuntimeError):
    """Git transport or repository isolation failed."""


def _open_components(path: Path) -> tuple[int, ...]:
    absolute = Path(os.path.abspath(path))
    descriptors = [os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY)]
    try:
        for component in absolute.parts[1:]:
            descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptors[-1],
            )
            descriptors.append(descriptor)
        return tuple(descriptors)
    except OSError as exc:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise GitTransportError("Git repository path is unsafe") from exc


class GitRunner:
    """Run Git against one retained repository directory without ambient config."""

    def __init__(self, repo: Path) -> None:
        self.repo = Path(repo)
        self._fds = _open_components(self.repo)
        info = os.fstat(self._fds[-1])
        self.identity = (info.st_dev, info.st_ino)
        self.environment = {
            "PATH": os.environ.get("PATH", ""), "LANG": "C", "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1", "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_LFS_SKIP_SMUDGE": "1",
        }

    @property
    def directory_fd(self) -> int:
        if not self._fds:
            raise GitTransportError("Git repository handle is closed")
        return self._fds[-1]

    def close(self) -> None:
        for descriptor in reversed(getattr(self, "_fds", ())):
            os.close(descriptor)
        self._fds = ()

    def __del__(self) -> None:
        self.close()

    def info(self) -> os.stat_result:
        return os.fstat(self.directory_fd)

    def has_path(self, path: str) -> bool:
        try:
            os.stat(path, dir_fd=self.directory_fd, follow_symlinks=False)
            return True
        except FileNotFoundError:
            return False

    def _execute(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        before = self.info()
        command = [
            "git", "-c", "credential.helper=", "-c", "core.hooksPath=",
            "-c", "core.useReplaceRefs=false", *args,
        ]
        cwd = os.path.join(os.sep, "proc", "self", "fd", str(self.directory_fd))
        result = subprocess.run(
            command, cwd=cwd, env=self.environment, capture_output=True,
            pass_fds=self._fds,
        )
        after = self.info()
        identities = ((before.st_dev, before.st_ino), (after.st_dev, after.st_ino))
        if any(identity != self.identity for identity in identities):
            raise GitTransportError("Git repository identity changed")
        return result

    def run(self, *args: str) -> bytes:
        result = self._execute(*args)
        if result.returncode:
            raise GitTransportError("Git operation failed")
        return result.stdout

    def optional(self, *args: str) -> bytes | None:
        result = self._execute(*args)
        if result.returncode not in {0, 1}:
            raise GitTransportError("Git operation failed")
        return result.stdout if result.returncode == 0 else None


def validate_private_modes(runner: GitRunner) -> None:
    """Require every retained mirror directory/file to be private and regular."""
    for _path, directories, files, directory_fd in os.fwalk(
            ".", follow_symlinks=False, dir_fd=runner.directory_fd):
        directory = os.fstat(directory_fd)
        if directory.st_uid != os.getuid() or stat.S_IMODE(directory.st_mode) != 0o700:
            raise GitTransportError("unsafe private mirror directory")
        for name in directories:
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
                    stat.S_IMODE(info.st_mode) != 0o700):
                raise GitTransportError("unsafe private mirror directory")
        for name in files:
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or
                    stat.S_IMODE(info.st_mode) not in {0o400, 0o600}):
                raise GitTransportError("unsafe private mirror file")


def require_empty_object_store(runner: GitRunner) -> None:
    """Reject preexisting loose, packed, or garbage objects in a fresh mirror."""
    values = {}
    for line in runner.run("count-objects", "-v").splitlines():
        if b": " in line:
            name, value = line.split(b": ", 1)
            values[name] = value
    for name in (b"count", b"in-pack", b"packs", b"size-pack", b"garbage"):
        if int(values.get(name, b"0")) != 0:
            raise GitTransportError("history audit requires an empty object store")
