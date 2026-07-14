"""Descriptor-relative, crash-safe private authority report transactions."""

from __future__ import annotations

import ctypes
import errno
import hashlib
import os
import stat
import uuid
from pathlib import Path, PurePosixPath

from .codec import encode_document
from .complete import CompleteIntegrityError, create_complete, verify_complete
from .coverage_contract import REQUIRED_REPORT_FILES

MAX_REPORT_FILE_BYTES = 100 * 1024 * 1024


class ReportTransactionError(OSError):
    """A private report transaction could not complete safely."""


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
        _close(descriptors)
        raise ReportTransactionError("private path is unsafe") from exc


def _close(descriptors: list[int] | tuple[int, ...]) -> None:
    for descriptor in reversed(descriptors):
        os.close(descriptor)


def _identities(descriptors: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple((info.st_dev, info.st_ino) for info in map(os.fstat, descriptors))


class _Directory:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.fds = _open_components(self.path)
        info = os.fstat(self.fds[-1])
        if (info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700):
            self.close()
            raise ReportTransactionError("unsafe private directory")
        self.identity = _identities(self.fds)

    @property
    def fd(self) -> int:
        if not self.fds:
            raise ReportTransactionError("private directory closed")
        return self.fds[-1]

    def close(self) -> None:
        _close(getattr(self, "fds", ()))
        self.fds = ()

    def matches_path(self) -> bool:
        try:
            current = _open_components(self.path)
        except ReportTransactionError:
            return False
        try:
            return _identities(current) == self.identity
        finally:
            _close(current)


def _name(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or not value.isascii() or path.is_absolute() or len(path.parts) != 1 or
            value in {".", "..", "COMPLETE"}):
        raise ReportTransactionError("invalid report filename")
    return value


def _transaction_id(value: str) -> str:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ReportTransactionError("invalid transaction ID") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise ReportTransactionError("invalid transaction ID")
    return value


def _open_child(parent_fd: int, name: str) -> int:
    descriptor = os.open(
        name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd
    )
    info = os.fstat(descriptor)
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        os.close(descriptor)
        raise ReportTransactionError("unsafe private child directory")
    return descriptor


def _exists(parent_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False


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


def _read_file(directory_fd: int, name: str) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
    try:
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or
                stat.S_IMODE(info.st_mode) != 0o600):
            raise ReportTransactionError("unsafe private report file")
        if info.st_size > MAX_REPORT_FILE_BYTES:
            raise ReportTransactionError("private report file too large")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(descriptor)


def _file_records(files: dict[str, bytes]) -> list[dict]:
    return [
        {"path": name, "sha256": hashlib.sha256(files[name]).hexdigest(),
         "size": len(files[name])}
        for name in REQUIRED_REPORT_FILES
    ]


def _rename_noreplace(parent_fd: int, source: str, target: str) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise ReportTransactionError("atomic no-replace rename unavailable")
    result = renameat2(
        parent_fd, source.encode("ascii"), parent_fd, target.encode("ascii"), 1
    )
    if result != 0:
        code = ctypes.get_errno()
        message = "report transaction already exists" if code == errno.EEXIST else "publish failed"
        raise ReportTransactionError(message)


def _rollback_publication(root_fd: int, final: str, incomplete: str) -> None:
    try:
        _rename_noreplace(root_fd, final, incomplete)
        directory_fd = _open_child(root_fd, incomplete)
        try:
            os.unlink("COMPLETE", dir_fd=directory_fd)
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise ReportTransactionError("published report rollback failed") from exc


def _prepare(root: _Directory, transaction_id: str,
             files: dict[str, bytes]) -> tuple[str, str, int]:
    final, incomplete = transaction_id, f".incomplete.{transaction_id}"
    if _exists(root.fd, final) or _exists(root.fd, incomplete):
        raise ReportTransactionError("report transaction already exists")
    os.mkdir(incomplete, 0o700, dir_fd=root.fd)
    directory_fd = _open_child(root.fd, incomplete)
    try:
        for name in REQUIRED_REPORT_FILES:
            _write_file(directory_fd, name, files[name])
    except OSError:
        os.close(directory_fd)
        raise
    return final, incomplete, directory_fd


def write_report(root: Path, transaction_id: str, files: dict[str, bytes],
                 complete_fields: dict, key: bytes) -> Path:
    """Write COMPLETE last and atomically publish without replacement."""
    transaction_id = _transaction_id(transaction_id)
    if complete_fields.get("transaction_id") != transaction_id:
        raise ReportTransactionError("transaction identity mismatch")
    if tuple(sorted(files)) != REQUIRED_REPORT_FILES or any(
            type(payload) is not bytes for payload in files.values()):
        raise ReportTransactionError("report file contract mismatch")
    directory = _Directory(Path(root))
    old_umask, published = os.umask(0o077), False
    final = incomplete = ""
    try:
        final, incomplete, report_fd = _prepare(directory, transaction_id, files)
        try:
            unsigned = {**complete_fields, "files": _file_records(files)}
            complete = encode_document("complete", create_complete(unsigned, key))
            _write_file(report_fd, "COMPLETE", complete)
            os.fsync(report_fd)
        finally:
            os.close(report_fd)
        if not directory.matches_path():
            raise ReportTransactionError("private parent changed")
        _rename_noreplace(directory.fd, incomplete, final)
        published = True
        try:
            os.fsync(directory.fd)
        except OSError:
            _rollback_publication(directory.fd, final, incomplete)
            published = False
            raise
        if not directory.matches_path():
            _rollback_publication(directory.fd, final, incomplete)
            published = False
            raise ReportTransactionError("private parent changed")
        return Path(root) / final
    except (OSError, ValueError) as exc:
        if not published and incomplete and _exists(directory.fd, incomplete):
            child = _open_child(directory.fd, incomplete)
            try:
                if _exists(child, "COMPLETE"):
                    os.unlink("COMPLETE", dir_fd=child)
            finally:
                os.close(child)
        if isinstance(exc, ReportTransactionError):
            raise
        raise ReportTransactionError("private report transaction failed") from exc
    finally:
        os.umask(old_umask)
        directory.close()


def verify_report(directory: Path, key: bytes, *, require_complete: bool = True) -> dict:
    """Authenticate exact COMPLETE inventory using descriptor-relative reads."""
    handle = _Directory(Path(directory))
    try:
        try:
            document = verify_complete(_read_file(handle.fd, "COMPLETE"), key)
        except (CompleteIntegrityError, ValueError) as exc:
            raise ReportTransactionError("invalid COMPLETE") from exc
        expected = {entry["path"]: entry for entry in document["files"]}
        if set(os.listdir(handle.fd)) != {*REQUIRED_REPORT_FILES, "COMPLETE"}:
            raise ReportTransactionError("private report inventory mismatch")
        for name in REQUIRED_REPORT_FILES:
            raw, record = _read_file(handle.fd, name), expected[name]
            if len(raw) != record["size"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
                raise ReportTransactionError("private report integrity mismatch")
        if require_complete and any(
                state != "scanned" for state in document["coverage_states"].values()):
            raise ReportTransactionError("private report coverage incomplete")
        return document
    finally:
        handle.close()


def cleanup_incomplete(root: Path, transaction_id: str) -> None:
    """Remove only a validated incomplete transaction without COMPLETE."""
    transaction_id = _transaction_id(transaction_id)
    handle, name = _Directory(Path(root)), f".incomplete.{transaction_id}"
    try:
        child = _open_child(handle.fd, name)
        try:
            if _exists(child, "COMPLETE"):
                raise ReportTransactionError("complete transaction cannot be cleaned")
            for entry in os.listdir(child):
                _read_file(child, _name(entry))
                os.unlink(entry, dir_fd=child)
            os.fsync(child)
        finally:
            os.close(child)
        os.rmdir(name, dir_fd=handle.fd)
        os.fsync(handle.fd)
    except OSError as exc:
        if isinstance(exc, ReportTransactionError):
            raise
        raise ReportTransactionError("incomplete cleanup failed") from exc
    finally:
        handle.close()
