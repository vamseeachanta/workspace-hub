"""Inventory regular files without modifying them. See README.md for the schema."""

import argparse
import fnmatch
import hashlib
import os
import stat
import sys
import time
from collections import defaultdict
from pathlib import Path

if __package__ in (None, ""):
    # Explicit repository bootstrap supports the required isolated (-I) invocation.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from dedupe._common import (
        FORMAT_VERSION,
        atomic_write_output,
        distinct_outputs,
        json_text,
        read_json,
        valid_digest,
    )
else:
    from ._common import (
        FORMAT_VERSION,
        atomic_write_output,
        distinct_outputs,
        json_text,
        read_json,
        valid_digest,
    )

# Issue #4224 task specification, slices 1–2; performance choices, not correctness inputs.
SAMPLE_BYTES = 64 * 1024
CHUNK_BYTES = 1024 * 1024


class BudgetExpired(Exception):
    """A cooperative deadline was reached."""


def signature(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def readonly_open(path, mode):
    """Reject symlink substitution and avoid blocking on substituted special files."""
    # Python 3.11 os.open: optional platform flags; zero means unavailable.
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    if path.is_symlink() or not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
        raise OSError("not a regular nonsymlink file")
    descriptor = os.open(path, flags)
    return os.fdopen(descriptor, mode)


def validate_config(config):
    if not isinstance(config, dict):
        raise TypeError("configuration must be an object")
    roots = config.get("roots")
    if (
        not isinstance(roots, list)
        or not roots
        or not all(isinstance(r, str) and r for r in roots)
    ):
        raise ValueError("roots must be a nonempty list of directory paths")
    if config.get("follow_symlinks", False) is not False:
        raise ValueError("only follow_symlinks=false is supported")
    minimum = config.get("min_size_bytes", 0)  # Issue #4224: zero includes empty files.
    if type(minimum) is not int or minimum < 0:
        raise ValueError("min_size_bytes must be a nonnegative integer")
    patterns = config.get("exclude", [])
    if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
        raise ValueError("exclude must be a list of globs")
    paths = [Path(r).absolute() for r in roots]
    if any(p.is_symlink() or not p.is_dir() for p in paths):
        raise ValueError("roots must be existing nonsymlink directories")
    paths = [p.resolve() for p in paths]
    for index, root in enumerate(paths):
        if any(root.is_relative_to(p) or p.is_relative_to(root) for p in paths[:index]):
            raise ValueError("roots must not overlap")
    return paths, minimum, patterns


def inventory(
    config,
    label,
    *,
    opener=readonly_open,
    clock=time.monotonic,
    max_seconds=None,
    cached=None,
    cache_result=None,
):
    """Return (file records, manifest header); hashing is injectable for I/O tests."""
    roots, minimum, excludes = validate_config(config)
    if not isinstance(label, str) or not label.strip():
        raise ValueError("label must be nonempty")
    if max_seconds is not None and (
        not isinstance(max_seconds, (int, float)) or not 0 < max_seconds < float("inf")
    ):
        raise ValueError("max_seconds must be finite and positive")
    cached = cached or {}
    start = clock()
    rows = []
    meta = {
        "type": "manifest",
        "version": FORMAT_VERSION,
        "label": label,
        "complete": True,
        "errors": [],
    }

    def check_budget():
        if max_seconds is not None and clock() - start >= max_seconds:
            raise BudgetExpired

    def excluded(path):
        return any(fnmatch.fnmatchcase(path, pattern) for pattern in excludes)

    def digest(row, full):
        check_budget()
        path = roots[row["root"]] / row["path"]
        with opener(path, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(before.st_mode)
                or signature(before) != row["_signature"]
            ):
                raise OSError("file changed")
            # FIPS 180-4 (2015), section 6.2: SHA-256, via stdlib hashlib.
            hasher = hashlib.sha256()
            if full:
                while True:
                    check_budget()
                    chunk = stream.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    hasher.update(chunk)
            else:
                hasher.update(stream.read(SAMPLE_BYTES))
                stream.seek(max(0, row["size"] - SAMPLE_BYTES))
                hasher.update(stream.read(SAMPLE_BYTES))
            if (
                signature(os.fstat(stream.fileno())) != row["_signature"]
                or signature(path.stat(follow_symlinks=False)) != row["_signature"]
            ):
                raise OSError("file changed")
            return hasher.hexdigest()

    def hash_group(members, full):
        for row in members:
            try:
                if row["sha256" if full else "sample_sha256"] is not None:
                    check_budget()
                    continue
                value = digest(row, full)
                row["sha256" if full else "sample_sha256"] = value
                row["stage"] = "full" if full else "sample"
            except OSError as exc:
                row["error"] = type(exc).__name__
                row["sha256"] = None
                row["sample_sha256"] = None
                row["stage"] = "size"
                meta["complete"] = False

    try:
        for root_index, root in enumerate(roots):
            pending = [root]
            while pending:
                check_budget()
                directory = pending.pop()
                try:
                    with os.scandir(directory) as entries:
                        children = sorted(entries, key=lambda e: e.name)
                    for entry in children:
                        check_budget()
                        relative = Path(entry.path).relative_to(root).as_posix()
                        if excluded(relative) or entry.is_symlink():
                            continue
                        try:
                            info = entry.stat(follow_symlinks=False)
                        except OSError as exc:
                            meta["complete"] = False
                            rows.append(
                                {
                                    "label": label,
                                    "root": root_index,
                                    "path": relative,
                                    "size": None,
                                    "mtime": None,
                                    "sha256": None,
                                    "sample_sha256": None,
                                    "stage": "size",
                                    "error": type(exc).__name__,
                                    "_signature": None,
                                }
                            )
                            continue
                        if stat.S_ISDIR(info.st_mode):
                            pending.append(Path(entry.path))
                        elif stat.S_ISREG(info.st_mode) and info.st_size >= minimum:
                            rows.append(
                                {
                                    "label": label,
                                    "root": root_index,
                                    "path": relative,
                                    "size": info.st_size,
                                    "mtime": info.st_mtime_ns,
                                    "sha256": None,
                                    "sample_sha256": None,
                                    "stage": "size",
                                    "_signature": signature(info),
                                }
                            )
                            row = rows[-1]
                            saved = cached.get(cache_key(row), {})
                            if saved.get("signature") == list(row["_signature"]):
                                for field in ("sample_sha256", "sha256"):
                                    value = saved.get(field)
                                    if value is not None and not valid_digest(value):
                                        raise ValueError("invalid cache digest")
                                if saved.get("sample_sha256"):
                                    row["sample_sha256"] = saved["sample_sha256"]
                                    row["stage"] = "sample"
                                    if saved.get("sha256"):
                                        row["sha256"] = saved["sha256"]
                                        row["stage"] = "full"
                except OSError as exc:
                    meta["complete"] = False
                    meta["errors"].append(
                        {
                            "root": root_index,
                            "path": directory.relative_to(root).as_posix(),
                            "error": type(exc).__name__,
                        }
                    )
        sizes = defaultdict(list)
        for row in rows:
            if "error" not in row:
                sizes[row["size"]].append(row)
        for members in sizes.values():
            if len(members) > 1:
                hash_group(members, full=False)
            else:
                row = members[0]
                row["sha256"] = None
                row["sample_sha256"] = None
                row["stage"] = "size"
        samples = defaultdict(list)
        for row in rows:
            if row["sample_sha256"] is not None and "error" not in row:
                samples[(row["size"], row["sample_sha256"])].append(row)
        for members in samples.values():
            if len(members) > 1:
                hash_group(members, full=True)
    except BudgetExpired:
        meta["complete"] = False
        meta["stop_reason"] = "budget"
    rows.sort(key=lambda r: (r["root"], r["path"]))
    for row in rows:
        if "error" not in row:
            try:
                path = roots[row["root"]] / row["path"]
                if signature(path.stat(follow_symlinks=False)) != row["_signature"]:
                    raise OSError("file changed")
            except OSError as exc:
                row["error"] = type(exc).__name__
                row["sha256"] = None
                row["sample_sha256"] = None
                row["stage"] = "size"
                meta["complete"] = False
        if cache_result is not None and "error" not in row and row["sample_sha256"]:
            cache_result[cache_key(row)] = {
                "signature": list(row["_signature"]),
                "sample_sha256": row["sample_sha256"],
                "sha256": row["sha256"],
            }
        row.pop("_signature")
    return rows, meta


def cache_key(row):
    # README.md, Cache schema: root, relative path, size and nanosecond mtime.
    return json_text([row["root"], row["path"], row["size"], row["mtime"]])


def run(config, label, out, *, cache=None, **kwargs):
    roots, _, _ = validate_config(config)
    distinct_outputs([out, cache], roots=roots)
    # Bind performance conventions and ordered roots; cache never substitutes other roots.
    context = hashlib.sha256(
        json_text(
            {
                "roots": [str(r) for r in roots],
                "version": FORMAT_VERSION,
                "sample_bytes": SAMPLE_BYTES,
                "algorithm": "sha256",
            }
        ).encode()
    ).hexdigest()
    cached = {}
    if cache is not None and Path(cache).exists():
        previous = read_json(cache)
        if not isinstance(previous, dict):
            raise ValueError("invalid cache")
        if previous.get("context") == context:
            cached = previous.get("entries", {})
            if not isinstance(cached, dict) or not all(
                isinstance(value, dict) for value in cached.values()
            ):
                raise ValueError("invalid cache entries")
    cache_result = dict(cached)
    rows, meta = inventory(
        config,
        label,
        cached=cached,
        cache_result=cache_result,
        **kwargs,
    )
    if cache is not None:
        atomic_write_output(
            cache,
            json_text(
                {
                    "context": context,
                    "entries": cache_result,
                }
            )
            + "\n",
        )
    atomic_write_output(out, "\n".join(json_text(r) for r in [meta, *rows]) + "\n")
    return rows, meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cache")
    parser.add_argument("--max-seconds", type=float)
    args = parser.parse_args()
    try:
        distinct_outputs([args.out, args.cache], inputs=[args.config])
        _, meta = run(
            read_json(args.config),
            args.label,
            args.out,
            cache=args.cache,
            max_seconds=args.max_seconds,
        )
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"inventory failed: {type(exc).__name__}\n")
    return 0 if meta["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
