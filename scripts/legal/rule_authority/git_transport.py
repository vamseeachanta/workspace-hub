"""Retained-dirfd, isolated Git transport for authority audits."""

from __future__ import annotations

import os
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
