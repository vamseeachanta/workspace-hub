"""No-follow filesystem primitives for a six-file, journaled copy transaction."""
import hashlib
import json
import os
from pathlib import Path
import stat


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, missing=False):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("root must be absolute without traversal")
    path = Path(os.path.abspath(path))
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if missing:
                continue
            raise ValueError("required path missing: " + str(current))
        validate_stat(info)
    return path


def validate_stat(info):
    if stat.S_ISLNK(info.st_mode):
        raise ValueError("symbolic link rejected")
    if os.name == "nt" and not hasattr(info, "st_file_attributes"):
        raise ValueError("Windows reparse evidence unavailable")
    if getattr(info, "st_file_attributes", 0) & 0x400 or getattr(info, "st_reparse_tag", 0):
        raise ValueError("reparse point rejected")
    if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
        raise ValueError("hard-linked file rejected")
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        raise ValueError("unsupported filesystem object")


def within(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("invalid relative payload path")
    p = Path(relative)
    if p.is_absolute() or any(x in {"..", "."} for x in p.parts):
        raise ValueError("payload traversal rejected")
    target = checked(root / p, missing=True)
    if not target.is_relative_to(root):
        raise ValueError("payload escapes root")
    return target


def preimage(path):
    checked(path, missing=True)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError("payload destination is not a regular file")
    return digest(path.read_bytes())


def disjoint(a, b):
    if a.is_relative_to(b) or b.is_relative_to(a):
        raise ValueError("source/destination subtrees overlap")


def volume(path):
    current = checked(path, missing=True)
    while not current.exists():
        current = current.parent
    return current.stat().st_dev


def validate_transaction(path, source, target):
    path = checked(path, missing=True)
    disjoint(path, source)
    disjoint(path, target)
    if volume(path) != volume(target):
        raise ValueError("transaction must share destination volume")
    return path


def durable_file(path, raw):
    checked(path, missing=True)
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def save_journal(transaction, receipt):
    checked(transaction)
    pending = transaction / "journal.pending"
    durable_file(pending, (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode())
    os.replace(pending, transaction / "journal.json")


def create_descendants(directory, target_root, transaction, receipt):
    if not directory.is_relative_to(target_root):
        raise ValueError("directory escapes destination project")
    current = target_root
    for part in directory.relative_to(target_root).parts:
        current /= part
        checked(current, missing=True)
        if current.exists():
            if not current.is_dir():
                raise ValueError("destination ancestor is not directory")
            continue
        item = {"path": current.relative_to(target_root).as_posix(), "created": False}
        receipt["directories"].append(item)
        save_journal(transaction, receipt)
        checked(current.parent)
        try:
            current.mkdir()
            item["created"] = True
        except FileExistsError:
            pass
        checked(current)
        if not current.is_dir():
            raise ValueError("concurrent non-directory creation")
        if item["created"]:
            item["identity"] = directory_identity(current)
        save_journal(transaction, receipt)


def directory_identity(path):
    info = checked(path).lstat()
    if not stat.S_ISDIR(info.st_mode) or not info.st_ino:
        raise ValueError("directory identity unavailable")
    return [info.st_dev, info.st_ino]


def replace_payload(staged, destination, expected):
    checked(staged)
    if preimage(destination) != expected:
        raise ValueError("destination changed immediately before replacement")
    os.replace(staged, destination)


def walk_no_links(root, directories=None):
    checked(root, missing=True)
    if not root.exists():
        return []
    found = []
    pending = [root]
    while pending:
        directory = pending.pop()
        checked(directory)
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                # Windows DirEntry.stat may omit nlink/inode; lstat supplies them.
                info = path.lstat()
                validate_stat(info)
                if stat.S_ISDIR(info.st_mode):
                    pending.append(path)
                    if directories is not None:
                        directories.append(path)
                elif entry.name == "SKILL.md":
                    found.append(path)
    return sorted(found)
