"""No-follow, no-overwrite private report transactions."""

from __future__ import annotations

import hashlib
import hmac
import ctypes
import os
import stat
import uuid
from contextlib import contextmanager
from pathlib import Path

from .codec import AuthorityError, canonical_bytes, parse_canonical


COMPLETE_DOMAIN = b"LEGAL-RULE-COMPLETE\0v1\0"
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_RENAME_NOREPLACE = 1


def _uuid(value):
    try:
        uuid.UUID(value)
    except (TypeError, ValueError) as exc:
        raise AuthorityError("filesystem") from exc


def _private_directory(path):
    flags = os.O_RDONLY | _DIRECTORY | _NOFOLLOW
    try:
        absolute = Path(path).absolute()
        fd = os.open(absolute.anchor or ".", flags)
        try:
            for component in absolute.parts[1:]:
                next_fd = os.open(component, flags, dir_fd=fd)
                os.close(fd)
                fd = next_fd
        except Exception:
            os.close(fd)
            raise
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode):
            raise OSError("not-directory")
        if os.name != "nt" and (
            info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700
        ):
            raise OSError("unsafe-directory")
        return fd, (info.st_dev, info.st_ino)
    except OSError as exc:
        raise AuthorityError("filesystem") from exc


def _check_same(fd, identity):
    info = os.fstat(fd)
    if (info.st_dev, info.st_ino) != identity:
        raise AuthorityError("filesystem")


def read_private_file(path, maximum):
    """Read a 0600 file through a retained 0700 parent directory handle."""
    target = Path(path)
    if os.name == "nt":
        try:
            if target.is_symlink() or target.parent.is_symlink():
                raise OSError("symlink")
            before = target.stat()
            if not target.is_file() or before.st_size > maximum:
                raise OSError("unsafe-file")
            data = target.read_bytes()
            after = target.stat()
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                raise OSError("changed-file")
            return data
        except OSError as exc:
            raise AuthorityError("filesystem") from exc
    parent_fd, identity = _private_directory(target.parent)
    file_fd = None
    try:
        file_fd = os.open(target.name, os.O_RDONLY | _NOFOLLOW, dir_fd=parent_fd)
        before = os.fstat(file_fd)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size > maximum
        ):
            raise OSError("unsafe-file")
        with os.fdopen(file_fd, "rb", closefd=False) as stream:
            data = stream.read(maximum + 1)
        after = os.fstat(file_fd)
        if len(data) > maximum or (before.st_dev, before.st_ino) != (
            after.st_dev,
            after.st_ino,
        ):
            raise OSError("changed-file")
        _check_same(parent_fd, identity)
        return data
    except OSError as exc:
        raise AuthorityError("filesystem") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(parent_fd)


def _sync_write_at(directory_fd, name, data):
    if Path(name).name != name or name in {"", ".", ".."}:
        raise AuthorityError("filesystem")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW
    try:
        fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
        try:
            with os.fdopen(fd, "wb", closefd=False) as stream:
                stream.write(data)
                stream.flush()
            os.fsync(fd)
            if os.name != "nt":
                info = os.fstat(fd)
                if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                    raise OSError("unsafe-file")
        finally:
            os.close(fd)
    except OSError as exc:
        raise AuthorityError("filesystem") from exc


def _rename_noreplace(directory_fd, source, destination):
    """Linux atomic no-replace directory rename; fail closed if unavailable."""
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = libc.renameat2
        renameat2.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        result = renameat2(
            directory_fd,
            os.fsencode(source),
            directory_fd,
            os.fsencode(destination),
            _RENAME_NOREPLACE,
        )
        if result != 0:
            raise OSError(ctypes.get_errno(), "renameat2")
    except (AttributeError, OSError) as exc:
        raise AuthorityError("filesystem") from exc


def _complete(files, key, identity, transaction_id, coverage, snapshots):
    records = [
        {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        for name, data in sorted(files.items())
    ]
    value = {
        "authority_revision": identity["authority_revision"],
        "coverage": coverage or {"result": "complete"},
        "files": records,
        "generation": identity["generation"],
        "schema_id": "legal-rule-" + "complete-v1",
        "snapshots": snapshots or {},
        "transaction_id": transaction_id,
    }
    value["manifest_mac"] = hmac.new(
        key, COMPLETE_DOMAIN + canonical_bytes(value), hashlib.sha256
    ).hexdigest()
    return value


def _verify_complete_value(value, files, key):
    required = {
        "authority_revision",
        "coverage",
        "files",
        "generation",
        "manifest_mac",
        "schema_id",
        "snapshots",
        "transaction_id",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AuthorityError("filesystem")
    mac = value["manifest_mac"]
    bare = {name: item for name, item in value.items() if name != "manifest_mac"}
    expected = hmac.new(
        key, COMPLETE_DOMAIN + canonical_bytes(bare), hashlib.sha256
    ).hexdigest()
    if not isinstance(mac, str) or not hmac.compare_digest(mac, expected):
        raise AuthorityError("filesystem")
    records = value["files"]
    if not isinstance(records, list) or [
        item.get("path") for item in records
    ] != sorted(files):
        raise AuthorityError("filesystem")
    for record in records:
        data = files.get(record.get("path"))
        if data is None or set(record) != {"path", "sha256", "size"}:
            raise AuthorityError("filesystem")
        if (
            record["size"] != len(data)
            or record["sha256"] != hashlib.sha256(data).hexdigest()
        ):
            raise AuthorityError("filesystem")
    return value


def _write_windows(parent, transaction_id, files, key, identity, coverage, snapshots):
    """Portable test/operator fallback; Linux is the hardened audit host."""
    parent = Path(parent)
    temporary = parent / f".incomplete.{transaction_id}"
    final = parent / transaction_id
    if (
        parent.is_symlink()
        or not parent.is_dir()
        or temporary.exists()
        or final.exists()
    ):
        raise AuthorityError("filesystem")
    try:
        temporary.mkdir()
        for name, data in {"marker": b"incomplete\n", **files}.items():
            if Path(name).name != name:
                raise OSError("unsafe-name")
            fd = os.open(temporary / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        complete = _complete(files, key, identity, transaction_id, coverage, snapshots)
        fd = os.open(
            temporary / "COMPLETE", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical_bytes(complete))
            stream.flush()
            os.fsync(stream.fileno())
        temporary.rename(final)
    except OSError as exc:
        raise AuthorityError("filesystem") from exc
    verify_complete_transaction(final, key)
    return final


def write_private_files(parent, files):
    """Write a bounded set of no-overwrite 0600 files into an existing 0700 dir."""
    parent = Path(parent)
    previous_umask = os.umask(0o077)
    if os.name == "nt":
        try:
            if parent.is_symlink() or not parent.is_dir():
                raise OSError("unsafe-directory")
            for name, data in sorted(files.items()):
                if Path(name).name != name:
                    raise OSError("unsafe-name")
                fd = os.open(parent / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            return
        except OSError as exc:
            raise AuthorityError("filesystem") from exc
        finally:
            os.umask(previous_umask)
    parent_fd = None
    try:
        parent_fd, identity = _private_directory(parent)
        for name, data in sorted(files.items()):
            _sync_write_at(parent_fd, name, data)
        os.fsync(parent_fd)
        _check_same(parent_fd, identity)
    finally:
        os.umask(previous_umask)
        if parent_fd is not None:
            os.close(parent_fd)


@contextmanager
def create_private_child(parent, name):
    """Create a no-overwrite 0700 child and retain stable parent/child handles."""
    if Path(name).name != name or name in {"", ".", ".."}:
        raise AuthorityError("filesystem")
    parent = Path(parent)
    if os.name == "nt":
        child = parent / name
        try:
            if parent.is_symlink() or not parent.is_dir():
                raise OSError("unsafe-parent")
            child.mkdir(mode=0o700)
            yield str(child), ()
        except OSError as exc:
            raise AuthorityError("filesystem") from exc
        return
    parent_fd, parent_identity = _private_directory(parent)
    child_fd = None
    previous_umask = os.umask(0o077)
    try:
        os.mkdir(name, 0o700, dir_fd=parent_fd)
        child_fd = os.open(name, os.O_RDONLY | _DIRECTORY | _NOFOLLOW, dir_fd=parent_fd)
        child_info = os.fstat(child_fd)
        if (
            child_info.st_uid != os.getuid()
            or stat.S_IMODE(child_info.st_mode) != 0o700
        ):
            raise OSError("unsafe-child")
        yield f"/proc/self/fd/{parent_fd}/{name}", (parent_fd, child_fd)
        _check_same(parent_fd, parent_identity)
        after = os.fstat(child_fd)
        if (after.st_dev, after.st_ino) != (child_info.st_dev, child_info.st_ino):
            raise AuthorityError("filesystem")
        os.fsync(child_fd)
        os.fsync(parent_fd)
    except (OSError, AuthorityError) as exc:
        raise AuthorityError("filesystem") from exc
    finally:
        os.umask(previous_umask)
        if child_fd is not None:
            os.close(child_fd)
        os.close(parent_fd)


def _verify_windows(directory, key):
    directory = Path(directory)
    try:
        if directory.is_symlink() or not directory.is_dir():
            raise OSError("unsafe-directory")
        names = sorted(item.name for item in directory.iterdir())
        if any(
            (directory / name).is_symlink() or not (directory / name).is_file()
            for name in names
        ):
            raise OSError("unsafe-entry")
        payloads = {name: (directory / name).read_bytes() for name in names}
        value = parse_canonical(payloads.pop("COMPLETE"))
        if payloads.pop("marker", None) != b"incomplete\n":
            raise OSError("missing-marker")
        return _verify_complete_value(value, payloads, key)
    except (OSError, KeyError, AuthorityError) as exc:
        raise AuthorityError("filesystem") from exc


def write_complete_transaction(
    parent, transaction_id, files, key, identity, *, coverage=None, snapshots=None
):
    """Create and fsync a COMPLETE transaction through retained directory handles."""
    _uuid(transaction_id)
    if set(files) & {"COMPLETE", "marker"} or not files:
        raise AuthorityError("filesystem")
    if os.name == "nt":
        return _write_windows(
            parent, transaction_id, files, key, identity, coverage, snapshots
        )
    parent = Path(parent)
    parent_fd, parent_identity = _private_directory(parent)
    temporary_name = f".incomplete.{transaction_id}"
    final_name = transaction_id
    child_fd = None
    previous_umask = os.umask(0o077)
    try:
        os.mkdir(temporary_name, 0o700, dir_fd=parent_fd)
        child_fd = os.open(
            temporary_name, os.O_RDONLY | _DIRECTORY | _NOFOLLOW, dir_fd=parent_fd
        )
        _sync_write_at(child_fd, "marker", b"incomplete\n")
        for name, data in sorted(files.items()):
            _sync_write_at(child_fd, name, data)
        complete = _complete(files, key, identity, transaction_id, coverage, snapshots)
        _sync_write_at(child_fd, "COMPLETE", canonical_bytes(complete))
        os.fsync(child_fd)
        _check_same(parent_fd, parent_identity)
        _rename_noreplace(parent_fd, temporary_name, final_name)
        os.fsync(parent_fd)
        _check_same(parent_fd, parent_identity)
    except (OSError, AuthorityError) as exc:
        raise AuthorityError("filesystem") from exc
    finally:
        os.umask(previous_umask)
        if child_fd is not None:
            os.close(child_fd)
        os.close(parent_fd)
    final = parent / final_name
    verify_complete_transaction(final, key)
    return final


def verify_complete_transaction(directory, key):
    if os.name == "nt":
        return _verify_windows(directory, key)
    directory = Path(directory)
    fd, identity = _private_directory(directory)
    try:
        names = sorted(os.listdir(fd))
        if "COMPLETE" not in names or "marker" not in names:
            raise AuthorityError("filesystem")
        payloads = {}
        for name in names:
            try:
                child = os.open(name, os.O_RDONLY | _NOFOLLOW, dir_fd=fd)
                info = os.fstat(child)
                if not stat.S_ISREG(info.st_mode):
                    raise OSError("not-regular")
                with os.fdopen(child, "rb") as stream:
                    data = stream.read()
            except OSError as exc:
                raise AuthorityError("filesystem") from exc
            payloads[name] = data
        value = parse_canonical(payloads.pop("COMPLETE"))
        if payloads.pop("marker", None) != b"incomplete\n":
            raise AuthorityError("filesystem")
        _check_same(fd, identity)
        return _verify_complete_value(value, payloads, key)
    except AuthorityError as exc:
        raise AuthorityError("filesystem") from exc
    finally:
        os.close(fd)


def cleanup_incomplete(parent, transaction_id):
    _uuid(transaction_id)
    if os.name == "nt":
        target = Path(parent) / f".incomplete.{transaction_id}"
        try:
            if (
                target.is_symlink()
                or (target / "marker").read_bytes() != b"incomplete\n"
            ):
                raise OSError("unsafe-incomplete")
            for item in target.iterdir():
                if item.is_symlink() or not item.is_file():
                    raise OSError("unsafe-entry")
                item.unlink()
            target.rmdir()
            return
        except OSError as exc:
            raise AuthorityError("filesystem") from exc
    parent_fd, parent_identity = _private_directory(parent)
    name = f".incomplete.{transaction_id}"
    child_fd = None
    try:
        child_fd = os.open(name, os.O_RDONLY | _DIRECTORY | _NOFOLLOW, dir_fd=parent_fd)
        entries = os.listdir(child_fd)
        if "marker" not in entries:
            raise AuthorityError("filesystem")
        marker_fd = os.open("marker", os.O_RDONLY | _NOFOLLOW, dir_fd=child_fd)
        with os.fdopen(marker_fd, "rb") as stream:
            if stream.read() != b"incomplete\n":
                raise AuthorityError("filesystem")
        for entry in entries:
            os.unlink(entry, dir_fd=child_fd)
        os.fsync(child_fd)
        os.close(child_fd)
        child_fd = None
        _check_same(parent_fd, parent_identity)
        os.rmdir(name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    except (OSError, AuthorityError) as exc:
        raise AuthorityError("filesystem") from exc
    finally:
        if child_fd is not None:
            os.close(child_fd)
        os.close(parent_fd)
