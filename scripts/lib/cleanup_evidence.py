"""Pinned evidence and descriptor-relative deletion under an exclusive writer lock.

The lock is a cooperation requirement, not protection against hostile writers.
Protocol constants and protected roles: docs/operations/cleanup-safety.html v1.
"""
import argparse
import base64
import fcntl
import hashlib
import json
import os
import stat
from pathlib import Path


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(fd):
    digest = hashlib.sha256()
    with os.fdopen(os.dup(fd), "rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):  # Buffer size only; no acceptance limit.
            digest.update(chunk)
    return digest.hexdigest()


def identity(value):
    # Atime can change during hashing; only stable identity/change fields are compared.
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


def record(parent, name, relative):
    before = os.stat(name, dir_fd=parent, follow_symlinks=False)
    result = {"path_b64": base64.b64encode(relative).decode("ascii"),
              "size": before.st_size, "mtime_ns": before.st_mtime_ns,
              "mode": stat.S_IMODE(before.st_mode), "device": before.st_dev,
              "inode": before.st_ino}
    if stat.S_ISREG(before.st_mode):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            if identity(os.fstat(fd)) != identity(before):
                raise ValueError("file changed while opening")
            result.update(kind="file", sha256=file_hash(fd))
            if identity(os.fstat(fd)) != identity(before):
                raise ValueError("file changed while hashing")
        finally:
            os.close(fd)
    elif stat.S_ISDIR(before.st_mode):
        result["kind"] = "directory"
    elif stat.S_ISLNK(before.st_mode):
        result.update(kind="symlink", link_b64=base64.b64encode(
            os.fsencode(os.readlink(name, dir_fd=parent))).decode("ascii"))
    else:
        raise ValueError("special files are not eligible")
    if identity(os.stat(name, dir_fd=parent, follow_symlinks=False)) != identity(before):
        raise ValueError("entry changed while recording")
    return result


def walk(parent, name, relative):
    row = record(parent, name, relative)
    rows = [row]
    if row["kind"] == "directory":
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            if (os.fstat(fd).st_ino, os.fstat(fd).st_dev) != (row["inode"], row["device"]):
                raise ValueError("directory changed while opening")
            for child in sorted(os.fsencode(item) for item in os.listdir(fd)):
                rows.extend(walk(fd, child, relative + b"/" + child))
            if record(parent, name, relative) != row:
                raise ValueError("directory changed while scanning")
        finally:
            os.close(fd)
    return rows


def snapshot_fd(fd, names):
    rows = []
    for name in sorted(os.fsencode(item) for item in names):
        if not name or name in (b".", b"..") or b"/" in name or b"\0" in name:
            raise ValueError("targets must be immediate trash children")
        rows.extend(walk(fd, name, name))
    return sorted(rows, key=lambda row: base64.b64decode(row["path_b64"]))


def snapshot(root, names):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return snapshot_fd(fd, names)
    finally:
        os.close(fd)


def protected(rows):
    for row in rows:
        parts = base64.b64decode(row["path_b64"]).lower().split(b"/")
        if any(part == b".git" or any(token in part for token in
               (b"verif", b"manifest", b"plan", b"test", b"review")) for part in parts):
            return True
    return False


def remove_tree(fd, name, expected, relative):
    """Re-hash each entry immediately before unlink; never follow a symlink."""
    row = record(fd, name, relative)
    if row != expected[relative]:
        raise ValueError("entry changed immediately before removal")
    if row["kind"] == "directory":
        child_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        try:
            opened = os.fstat(child_fd)
            if (opened.st_dev, opened.st_ino) != (row["device"], row["inode"]):
                raise ValueError("directory replaced while opening for removal")
            for child in sorted(os.fsencode(item) for item in os.listdir(child_fd)):
                remove_tree(child_fd, child, expected, relative + b"/" + child)
        finally:
            os.close(child_fd)
        current = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != (row["device"], row["inode"]):
            raise ValueError("directory replaced before removal")
        os.rmdir(name, dir_fd=fd)
    else:
        os.unlink(name, dir_fd=fd)


def purge(root, artifact, artifact_sha256, execute=False):
    result = {"removed": [], "retained": [], "reason": ""}
    fd = None
    try:
        root, artifact = Path(root), Path(artifact)
        data_bytes = artifact.read_bytes()
        if digest_bytes(data_bytes) != artifact_sha256:
            raise ValueError("verification artifact digest mismatch")
        data = json.loads(data_bytes)
        if not isinstance(data, dict):
            raise TypeError("verification artifact must be an object")
        names = data["target_paths"]
        if (not isinstance(names, list) or any(not isinstance(name, str) for name in names)
                or not isinstance(data.get("entries"), list)):
            raise ValueError("verification artifact requires target and entry lists")
        result["retained"] = list(names)
        if (type(data["schema"]) is not int or data["schema"] != 1
                or data["delete_allowed"] is not True
                or not names or len(names) != len(set(names))):
            raise ValueError("invalid deletion permission")
        for name in names:
            if artifact.resolve().is_relative_to((root / name).resolve()):
                raise ValueError("verification artifact is within deletion target")
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rows = snapshot_fd(fd, names)
        if protected(rows):
            raise ValueError("protected evidence or repository artifact")
        if rows != data["entries"]:
            raise ValueError("paths, metadata or content changed since verification")
        if not execute:
            result["reason"] = "dry run; verified targets retained"
            return result
        # Re-read the pinned artifact and all contents under the lock, before removal.
        if artifact.read_bytes() != data_bytes or snapshot_fd(fd, names) != rows:
            raise ValueError("evidence changed before removal")
        expected = {base64.b64decode(row["path_b64"]): row for row in rows}
        for name in names:
            remove_tree(fd, os.fsencode(name), expected, os.fsencode(name))
            result["removed"].append(name)
            result["retained"].remove(name)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result["reason"] = str(error)
        if not result["retained"]:
            result["retained"] = ["all unverified staged evidence"]
    finally:
        if fd is not None:
            os.close(fd)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("digest")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    print(json.dumps(purge(args.root, args.artifact, args.digest, args.execute)))
