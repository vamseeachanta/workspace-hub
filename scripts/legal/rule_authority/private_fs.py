"""Fail-closed loading of the private HMAC key."""

from __future__ import annotations

import base64
import binascii
import os
import stat
from pathlib import Path
from typing import Mapping


class PrivateFilesystemError(OSError):
    """Private input violates ownership, mode, or no-follow requirements."""


def _decode_key(text: str, trailing_lf: bool) -> bytes:
    if trailing_lf:
        if not text.endswith("\n") or "\n" in text[:-1]:
            raise PrivateFilesystemError("invalid key encoding")
        text = text[:-1]
    elif "\n" in text or "\r" in text:
        raise PrivateFilesystemError("invalid key encoding")
    try:
        decoded = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise PrivateFilesystemError("invalid key encoding") from exc
    if len(decoded) != 32 or base64.b64encode(decoded).decode("ascii") != text:
        raise PrivateFilesystemError("invalid key encoding")
    return decoded


def _check_metadata(info: os.stat_result, required_mode: int) -> None:
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != required_mode:
        raise PrivateFilesystemError("unsafe private file metadata")


def _close_all(descriptors: list[int] | tuple[int, ...]) -> None:
    for descriptor in reversed(descriptors):
        os.close(descriptor)


def _identities(descriptors: list[int] | tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple((info.st_dev, info.st_ino) for info in map(os.fstat, descriptors))


def _open_parent(path: Path) -> tuple[int, ...]:
    absolute = Path(os.path.abspath(path))
    descriptors = [os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY)]
    private_boundary = False
    try:
        for component in absolute.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=descriptors[-1])
            info = os.fstat(child)
            mode = stat.S_IMODE(info.st_mode)
            if private_boundary or (info.st_uid == os.getuid() and mode == 0o700):
                if not private_boundary:
                    _close_all(descriptors)
                    descriptors = [child]
                else:
                    descriptors.append(child)
                private_boundary = True
                _check_metadata(info, 0o700)
            else:
                _close_all(descriptors)
                descriptors = [child]
        _check_metadata(os.fstat(descriptors[-1]), 0o700)
        return tuple(descriptors)
    except Exception:
        _close_all(descriptors)
        raise


def _read_key_at(parent_fd: int, name: str) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise PrivateFilesystemError("key is not a regular file")
        _check_metadata(info, 0o600)
        raw = os.read(descriptor, 1024)
        if os.read(descriptor, 1):
            raise PrivateFilesystemError("key file too large")
        return raw
    finally:
        os.close(descriptor)


def _parent_path_matches(path: Path, expected: tuple[tuple[int, int], ...]) -> bool:
    descriptors = _open_parent(path)
    try:
        return expected == _identities(descriptors)
    finally:
        _close_all(descriptors)


def _load_key_file(path: Path) -> bytes:
    try:
        parent_fds = _open_parent(path)
        try:
            before = _identities(parent_fds)
            raw = _read_key_at(parent_fds[-1], Path(path).name)
            stable_fd = before == _identities(parent_fds)
            if not stable_fd or not _parent_path_matches(path, before):
                raise PrivateFilesystemError("private parent changed")
        finally:
            _close_all(parent_fds)
    except (OSError, UnicodeError) as exc:
        if isinstance(exc, PrivateFilesystemError):
            raise
        raise PrivateFilesystemError("cannot read private key") from exc
    return _decode_key(raw.decode("ascii"), trailing_lf=True)


def load_key(*, key_file: Path | None, env_name: str | None,
             environ: Mapping[str, str]) -> bytes:
    """Load exactly one canonical 32-byte key without logging its locator/value."""
    if (key_file is None) == (env_name is None):
        raise PrivateFilesystemError("select exactly one key source")
    if key_file is not None:
        return _load_key_file(Path(key_file))
    if env_name not in environ:
        raise PrivateFilesystemError("selected key source unavailable")
    return _decode_key(environ[env_name], trailing_lf=False)
