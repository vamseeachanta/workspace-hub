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


def _load_key_file(path: Path) -> bytes:
    try:
        parent_info = path.parent.lstat()
        if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode):
            raise PrivateFilesystemError("unsafe private parent")
        _check_metadata(parent_info, 0o700)
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode):
                raise PrivateFilesystemError("key is not a regular file")
            _check_metadata(info, 0o600)
            raw = os.read(descriptor, 1024)
            if os.read(descriptor, 1):
                raise PrivateFilesystemError("key file too large")
        finally:
            os.close(descriptor)
    except (OSError, UnicodeError) as exc:
        if isinstance(exc, PrivateFilesystemError):
            raise
        raise PrivateFilesystemError("cannot read private key") from exc
    return _decode_key(raw.decode("ascii"), trailing_lf=True)


def load_key(*, key_file: Path | None, env_name: str | None,
             environ: Mapping[str, str]) -> bytes:
    """Load exactly one canonical 32-byte key without logging its locator/value."""
    env_selected = env_name is not None and env_name in environ
    if (key_file is not None) == env_selected:
        raise PrivateFilesystemError("select exactly one key source")
    if key_file is not None:
        return _load_key_file(Path(key_file))
    return _decode_key(environ[env_name], trailing_lf=False)
