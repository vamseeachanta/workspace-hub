"""Canonical CI envelope decoder with no-overwrite private output."""

from __future__ import annotations

import base64
import os
import stat
from pathlib import Path

from .codec import AuthorityError, parse_canonical


FIELDS = {"anchor", "key", "ledger", "manifest", "map", "schema_id"}


def materialize(data, out_dir):
    value = parse_canonical(data, 32768)
    if (
        not isinstance(value, dict)
        or set(value) != FIELDS
        or value["schema_id"] != "legal-rule-ci-envelope-v1"
    ):
        raise AuthorityError("schema")
    output = Path(out_dir)
    previous_umask = os.umask(0o077)
    try:
        info = output.stat(follow_symlinks=False)
        if not stat.S_ISDIR(info.st_mode) or output.is_symlink():
            raise OSError("unsafe-directory")
        if os.name != "nt" and (
            info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700
        ):
            raise OSError("unsafe-directory")
        for field in ("anchor", "ledger", "manifest", "map", "key"):
            encoded = value[field]
            try:
                decoded = base64.b64decode(encoded, validate=True)
            except Exception as exc:
                raise AuthorityError("schema") from exc
            if base64.b64encode(decoded).decode("ascii") != encoded:
                raise AuthorityError("schema")
            suffix = "b64" if field == "key" else "json"
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(output / f"{field}.{suffix}", flags, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(decoded)
                stream.flush()
                os.fsync(stream.fileno())
    except AuthorityError:
        raise
    except OSError as exc:
        raise AuthorityError("filesystem") from exc
    finally:
        os.umask(previous_umask)
