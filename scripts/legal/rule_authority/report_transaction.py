"""Crash-safe private authority audit report transactions."""

from __future__ import annotations

import hashlib
import os
import stat
import uuid
from pathlib import Path, PurePosixPath

from .codec import encode_document
from .complete import CompleteIntegrityError, create_complete, verify_complete


class ReportTransactionError(OSError):
    """A private report transaction could not complete safely."""


def _check_root(root: Path) -> None:
    try:
        info = root.lstat()
    except OSError as exc:
        raise ReportTransactionError("private report root unavailable") from exc
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
            stat.S_IMODE(info.st_mode) != 0o700):
        raise ReportTransactionError("unsafe private report root")


def _name(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or not value.isascii() or path.is_absolute() or len(path.parts) != 1 or
            value in {".", "..", "COMPLETE"}):
        raise ReportTransactionError("invalid report filename")
    return value


def _write_file(directory_fd: int, name: str, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    descriptor = os.open(name, flags, 0o600, dir_fd=directory_fd)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ReportTransactionError("private report write failed")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _file_records(files: dict[str, bytes]) -> list[dict]:
    return [
        {"path": name, "sha256": hashlib.sha256(files[name]).hexdigest(),
         "size": len(files[name])}
        for name in sorted(files)
    ]


def _transaction_id(value: str) -> str:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ReportTransactionError("invalid transaction ID") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise ReportTransactionError("invalid transaction ID")
    return value


def write_report(root: Path, transaction_id: str, files: dict[str, bytes],
                 complete_fields: dict, key: bytes) -> Path:
    """Write files and authenticated COMPLETE last, then atomically publish."""
    root = Path(root)
    _check_root(root)
    transaction_id = _transaction_id(transaction_id)
    if complete_fields.get("transaction_id") != transaction_id:
        raise ReportTransactionError("transaction identity mismatch")
    checked = {_name(name): payload for name, payload in files.items()}
    if any(type(payload) is not bytes for payload in checked.values()):
        raise ReportTransactionError("invalid report payload")
    final = root / transaction_id
    incomplete = root / f".incomplete.{transaction_id}"
    if final.exists() or incomplete.exists():
        raise ReportTransactionError("report transaction already exists")
    old_umask = os.umask(0o077)
    try:
        incomplete.mkdir(mode=0o700)
        directory_fd = os.open(incomplete, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for name in sorted(checked):
                _write_file(directory_fd, name, checked[name])
            unsigned = dict(complete_fields)
            unsigned["files"] = _file_records(checked)
            complete = encode_document("complete", create_complete(unsigned, key))
            _write_file(directory_fd, "COMPLETE", complete)
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        try:
            os.replace(incomplete, final)
        except OSError:
            (incomplete / "COMPLETE").unlink(missing_ok=True)
            raise
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(root_fd)
        finally:
            os.close(root_fd)
        return final
    except (OSError, ValueError) as exc:
        if isinstance(exc, ReportTransactionError):
            raise
        raise ReportTransactionError("private report transaction failed") from exc
    finally:
        os.umask(old_umask)


def _read_private(path: Path) -> bytes:
    try:
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or
                stat.S_IMODE(info.st_mode) != 0o600):
            raise ReportTransactionError("unsafe private report file")
        return path.read_bytes()
    except OSError as exc:
        if isinstance(exc, ReportTransactionError):
            raise
        raise ReportTransactionError("private report unreadable") from exc


def verify_report(directory: Path, key: bytes, *, require_complete: bool = True) -> dict:
    """Authenticate COMPLETE and reject extra, missing, or changed report files."""
    directory = Path(directory)
    _check_root(directory)
    try:
        document = verify_complete(_read_private(directory / "COMPLETE"), key)
    except (CompleteIntegrityError, ValueError) as exc:
        raise ReportTransactionError("invalid COMPLETE") from exc
    expected = {entry["path"]: entry for entry in document["files"]}
    try:
        actual = {entry.name for entry in directory.iterdir()}
    except OSError as exc:
        raise ReportTransactionError("private report unreadable") from exc
    if actual != {*expected, "COMPLETE"}:
        raise ReportTransactionError("private report inventory mismatch")
    for name, record in expected.items():
        raw = _read_private(directory / name)
        if len(raw) != record["size"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
            raise ReportTransactionError("private report integrity mismatch")
    if require_complete and any(state != "scanned" for state in document["coverage_states"].values()):
        raise ReportTransactionError("private report coverage incomplete")
    return document
