"""No-overwrite private report transactions."""

from __future__ import annotations

import hashlib
import hmac
import os
import shutil
import uuid
from pathlib import Path

from .codec import AuthorityError, canonical_bytes


COMPLETE_DOMAIN = b"LEGAL-RULE-COMPLETE\0v1\0"


def _sync_write(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if os.name != "nt":
        os.chmod(path, 0o600)


def _complete(files, key, identity, transaction_id):
    records = [
        {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        for name, data in sorted(files.items())
    ]
    value = {
        "authority_revision": identity["authority_revision"],
        "coverage": "complete",
        "files": records,
        "generation": identity["generation"],
        "schema_id": "legal-rule-complete-v1",
        "transaction_id": transaction_id,
    }
    value["manifest_mac"] = hmac.new(
        key, COMPLETE_DOMAIN + canonical_bytes(value), hashlib.sha256
    ).hexdigest()
    return value


def write_complete_transaction(parent, transaction_id, files, key, identity):
    try:
        uuid.UUID(transaction_id)
    except ValueError as exc:
        raise AuthorityError("filesystem") from exc
    parent = Path(parent)
    if not parent.is_dir() or (os.name != "nt" and parent.stat().st_mode & 0o077):
        raise AuthorityError("filesystem")
    temporary = parent / f".incomplete.{transaction_id}"
    final = parent / transaction_id
    if final.exists() or temporary.exists() or parent.is_symlink():
        raise AuthorityError("filesystem")
    try:
        temporary.mkdir(mode=0o700)
        _sync_write(temporary / "marker", b"incomplete\n")
        for name, data in files.items():
            if Path(name).name != name:
                raise AuthorityError("filesystem")
            _sync_write(temporary / name, data)
        complete = _complete(files, key, identity, transaction_id)
        _sync_write(temporary / "COMPLETE", canonical_bytes(complete))
        temporary.replace(final)
        return final
    except (OSError, AuthorityError) as exc:
        raise AuthorityError("filesystem") from exc


def cleanup_incomplete(parent, transaction_id):
    try:
        uuid.UUID(transaction_id)
    except ValueError as exc:
        raise AuthorityError("filesystem") from exc
    target = Path(parent) / f".incomplete.{transaction_id}"
    marker = target / "marker"
    if (
        target.is_symlink()
        or not marker.is_file()
        or marker.read_bytes() != b"incomplete\n"
    ):
        raise AuthorityError("filesystem")
    shutil.rmtree(target)
