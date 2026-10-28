"""UTF-8 atomic replacement with observable-state checks and conditional recovery.

Only regular files or absent destinations are accepted. Sibling staging uses
POSIX permission flags (stat.S_IMODE); new files retain mkstemp's private mode.
SHA-256 receipts use hashlib. No file contents are included in error messages.

These checks are conditional, not a filesystem compare-and-swap: another writer
can act between the last observation and replace, including during recovery.
Callers requiring exclusion must serialize writers externally. Identical-byte
changes and changes before entry are not reliably detected. File fsync does not
provide directory-entry crash durability; ACLs, ownership and extended attributes
are not preserved. Windows sharing rules can prevent replacement.
"""

import hashlib
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class _Snapshot:
    data: bytes
    mode: int
    stamp: tuple[int, ...]
    key: tuple[int, int]


def _stamp(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev, info.st_ino, info.st_mode, info.st_size,
        info.st_mtime_ns, info.st_ctime_ns,
    )


def _snapshot(path: Path) -> _Snapshot | None:
    try:
        initial = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(initial.st_mode):
        raise ValueError("destination must be a regular file")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if _stamp(initial) != _stamp(opened):
            raise OSError("destination changed while opening")
        data = stream.read()
        finished = os.fstat(stream.fileno())
    if _stamp(initial) != _stamp(finished) or _stamp(initial) != _stamp(path.lstat()):
        raise OSError("destination changed while reading")
    return _Snapshot(
        data, stat.S_IMODE(initial.st_mode), _stamp(initial),
        (initial.st_dev, initial.st_ino),
    )


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AtomicWriteError(RuntimeError):
    """Failure receipt plus original bytes/mode for explicit manual recovery.

    before_bytes is retained in memory only and may contain sensitive state.
    Receipt digests do not establish that the destination still has those bytes.
    """

    def __init__(self, message: str, receipt: dict, before: _Snapshot | None):
        super().__init__(message)
        self.receipt = receipt
        self.before_bytes = before.data if before is not None else None
        self.before_mode = before.mode if before is not None else None


class ConcurrentChangeError(AtomicWriteError):
    """An observed destination change prevented replacement."""


def _cleanup(temporary: Path, receipt: dict) -> None:
    """Retain cleanup evidence without masking the primary failure."""
    try:
        temporary.unlink(missing_ok=True)
    except OSError as error:
        receipt.setdefault("cleanup_errors", []).append({
            "error": type(error).__name__,
            "retained_path": temporary.as_posix(),
        })


def _stage(path: Path, data: bytes, mode: int | None, receipt: dict) -> Path:
    """Fully write and sync a sibling; remove it if staging fails."""
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temporary = Path(name)
    try:
        try:
            remaining = memoryview(data)
            while remaining:
                count = os.write(fd, remaining)
                # POSIX write: zero bytes means no progress; negatives are invalid.
                if count <= 0:
                    raise OSError("staging write made no progress")
                remaining = remaining[count:]
            if mode is not None:
                os.chmod(temporary, mode)
            os.fsync(fd)
        finally:
            os.close(fd)
        return temporary
    except BaseException:
        _cleanup(temporary, receipt)
        raise


def _owns(current: _Snapshot | None, staged: _Snapshot) -> bool:
    return (
        current is not None and current.key == staged.key
        and current.data == staged.data and current.mode == staged.mode
    )


def _recover(path: Path, before: _Snapshot | None, staged: _Snapshot, receipt: dict) -> None:
    """Restore only an observed matching installed file; never restore over a mismatch."""
    if before is None:
        # There is no previous file to restore; retain the attempted file for inspection.
        receipt["recovery"] = "not_available"
        return
    temporary = None
    try:
        current = _snapshot(path)
        if not _owns(current, staged):
            receipt["recovery"] = "refused"
            return
        temporary = _stage(path, before.data, before.mode, receipt)
        if _snapshot(path) != current:
            receipt["recovery"] = "refused"
            return
        os.replace(temporary, path)
        temporary = None
        restored = _snapshot(path)
        if restored is None or restored.data != before.data or restored.mode != before.mode:
            raise OSError("recovery readback mismatch")
        receipt["restored_sha"] = _sha(restored.data)
        receipt["recovery"] = "restored"
    except (OSError, ValueError) as error:
        receipt["recovery"] = "failed"
        receipt["recovery_error"] = type(error).__name__
    finally:
        if temporary is not None:
            _cleanup(temporary, receipt)


def atomic_write_utf8(path: Path | str, content: str) -> dict:
    """Encode before touching the destination, replace, and verify bytes and mode.

    The parent directory must exist. UnicodeEncodeError propagates before any
    filesystem access. Initial snapshot errors propagate without mutation.
    Later I/O failures raise AtomicWriteError with before/attempted/restored
    digest receipts and the in-memory original. Cleanup failures add error types
    and retained sibling paths to cleanup_errors without masking that exception.
    A successful receipt additionally
    has written_sha. Recovery is attempted after readback failure only, and only
    if the installed inode, bytes and mode still match. Observed unrelated bytes
    are retained. This does not eliminate the check-to-replace race.
    """
    data = content.encode("utf-8")
    path = Path(path)
    before = _snapshot(path)
    receipt = {
        "path": path.as_posix(),
        "before_sha": _sha(before.data) if before is not None else None,
        "attempted_sha": _sha(data),
        "written_sha": None,
        "restored_sha": None,
        "recovery": "not_needed",
    }
    temporary = None
    try:
        temporary = _stage(path, data, before.mode if before is not None else None, receipt)
        staged = _snapshot(temporary)
        if staged is None or staged.data != data:
            raise OSError("staging readback mismatch")
        if before is not None and staged.mode != before.mode:
            raise OSError("staging mode mismatch")
        if _snapshot(path) != before:
            raise ConcurrentChangeError("destination changed before replacement", receipt, before)
        os.replace(temporary, path)
        temporary = None
        try:
            written = _snapshot(path)
            if not _owns(written, staged):
                raise OSError("destination readback mismatch")
        except (OSError, ValueError) as error:
            _recover(path, before, staged, receipt)
            raise AtomicWriteError("destination readback failed", receipt, before) from error
        receipt["written_sha"] = _sha(written.data)
        return receipt
    except (OSError, ValueError) as error:
        raise AtomicWriteError("atomic replacement failed", receipt, before) from error
    finally:
        if temporary is not None:
            _cleanup(temporary, receipt)
