#!/usr/bin/env python3
"""Inventory metadata outside configured repositories and cache directories."""

from __future__ import annotations

import argparse
import fnmatch
import json
import math
import os
import stat
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path


def validate(config):
    if not isinstance(config, dict):
        raise TypeError("config must be a JSON object")
    if not isinstance(config.get("root"), str) or not config["root"]:
        raise ValueError("root must be a nonempty directory string")
    for key in ("repos", "cache_allow"):
        values = config.get(key, [])
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value for value in values
        ):
            raise ValueError(f"{key} must be a list of nonempty strings")
    limit = config.get("max_files")
    if type(limit) is not int or limit < 0:
        raise ValueError("max_files must be a nonnegative integer")
    if type(config.get("follow_symlinks", False)) is not bool:
        raise ValueError("follow_symlinks must be boolean")


def is_link(path):
    """Treat directory junctions and other Windows reparse points as links."""
    return (
        path.is_symlink()
        or getattr(path, "is_junction", lambda: False)()
        or (
            os.name == "nt"
            and path.exists()
            and bool(
                path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
            )
        )
    )


def scan(config):
    """One deterministic traversal; no file content reads, including Git markers.

    Python 3.11 os.scandir/stat docs define the metadata and inode semantics:
    https://docs.python.org/3.11/library/os.html#os.scandir
    """
    validate(config)
    root = Path(config["root"]).resolve()
    if not root.is_dir():
        raise ValueError("root does not exist or is not a directory")
    declared = {(root / item).resolve() for item in config.get("repos", [])}
    if any(not path.is_dir() for path in declared):
        raise ValueError("a configured repository directory does not exist")
    automatic = not declared
    if automatic:
        for ancestor in (root, *root.parents):
            marker = ancestor / ".git"
            # A root marker is queried even if malformed; ancestors must have
            # an initialized Git directory or a worktree marker, not an empty dir.
            if marker.is_file() or (
                marker.is_dir() and (ancestor == root or (marker / "HEAD").is_file())
            ):
                return [], [ancestor]
    repos = set(declared)
    seen = set()
    files = []
    follow = config.get("follow_symlinks", False)

    def cache(path):
        relative = path.relative_to(root).as_posix()
        return any(
            fnmatch.fnmatchcase(path.name, pattern)
            or fnmatch.fnmatchcase(relative, pattern)
            for pattern in config.get("cache_allow", [])
        )

    def repository(path):
        marker = path / ".git"
        return any(path.is_relative_to(repo) for repo in declared) or (
            automatic and (marker.is_dir() or marker.is_file())
        )

    def excluded_target(target):
        if not target.is_relative_to(root):
            return True
        parents = [target] if target.is_dir() else []
        parents += list(target.parents)
        return any(
            cache(parent) or repository(parent)
            for parent in parents
            if parent.is_relative_to(root)
        )

    stack = [root]
    while stack:
        directory = stack.pop()
        resolved = directory.resolve()
        if repository(resolved):
            if automatic:
                repos.add(resolved)
            continue
        if cache(directory) or cache(resolved):
            continue
        info = directory.stat()
        identity = (info.st_dev, info.st_ino)
        if identity in seen:
            continue
        seen.add(identity)
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda entry: entry.name)
        directories = []
        for entry in children:
            path = Path(entry.path)
            if is_link(path):
                if not follow:
                    continue
                # Resolve loops and dangling links without opening their targets.
                try:
                    target = path.resolve(strict=True)
                except (OSError, RuntimeError):
                    continue
                if excluded_target(target):
                    continue
            info = entry.stat(follow_symlinks=follow)
            if stat.S_ISDIR(info.st_mode):
                directories.append(path)
            elif stat.S_ISREG(info.st_mode):
                files.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "size": info.st_size,
                        "mtime": info.st_mtime,
                    }
                )
                if len(files) > config["max_files"]:
                    raise ValueError("max_files exceeded; no complete inventory")
        stack.extend(reversed(directories))
    return sorted(files, key=lambda item: item["path"]), sorted(repos)


# Extension lists are local conventions, not standards; see README Configuration.
# Custom tables replace these defaults. No filename-based default is assumed.
DEFAULT_CATEGORIES = {
    "script": {"extensions": [".py", ".sh", ".js", ".ps1", ".bat"]},
    "document": {"extensions": [".txt", ".md", ".rst", ".pdf", ".docx"]},
    "data": {"extensions": [".csv", ".json", ".yaml", ".yml", ".xml", ".parquet"]},
    "image": {"extensions": [".png", ".jpg", ".jpeg", ".svg", ".gif"]},
    "archive": {"extensions": [".zip", ".gz", ".tar", ".bz2", ".xz"]},
    "log": {"extensions": [".log"]},
    "build output": {"extensions": [".o", ".obj", ".so", ".dll", ".pyc"]},
    "unknown": {"extensions": []},
}
# Local display convention: retain at most 20 records per largest-file list.
LARGEST_COUNT = 20
# Format revision chosen here; README, Manifest format, defines schema 1.
SCHEMA = 1


def category_table(config):
    table = config.get("categories", DEFAULT_CATEGORIES)
    if not isinstance(table, dict) or not table:
        raise ValueError("categories must be a nonempty object")
    extensions, names = {}, {}
    for category, rule in table.items():
        if category not in DEFAULT_CATEGORIES or not isinstance(rule, dict):
            raise ValueError("invalid category rule")
        if set(rule) - {"extensions", "names"}:
            raise ValueError("unknown category rule key")
        for field, mapping in (("extensions", extensions), ("names", names)):
            values = rule.get(field, [])
            if not isinstance(values, list):
                raise TypeError("category mappings must be lists")
            for value in values:
                if not isinstance(value, str) or not value or "/" in value:
                    raise ValueError("invalid category mapping")
                key = value.casefold()
                if field == "extensions" and not key.startswith("."):
                    raise ValueError("extensions must start with a dot")
                if key in mapping:
                    raise ValueError("duplicate category mapping")
                mapping[key] = category
    return extensions, names


def aggregate(files):
    times = [item["mtime"] for item in files]
    return {
        "count": len(files),
        "bytes": sum(item["size"] for item in files),
        "oldest_mtime": min(times) if times else None,
        "newest_mtime": max(times) if times else None,
        "largest_files": sorted(files, key=lambda item: (-item["size"], item["path"]))[
            :LARGEST_COUNT
        ],
    }


def repository_state(path, cutoff):
    """Read-only Git evidence; no fetch, lock, index refresh or content scan.

    Git manuals: git-status, Porcelain Format Version 1 (-z rename records);
    git-log, --all/--not/--remotes and %ct (committer Unix timestamp).
    Remote reachability uses locally recorded refs, not network visibility.
    """
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["LC_ALL"] = "C"

    def git(*args):
        result = subprocess.run(
            [
                "git",
                "-c",
                "core.fsmonitor=false",
                "-c",
                "core.untrackedCache=false",
                "-C",
                str(path),
                *args,
            ],
            env=env,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            # Never reproduce Git diagnostics: they can contain private paths.
            raise ValueError("Git query failed; repository counters unavailable")
        return result.stdout

    records = iter(
        git("status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    )
    dirty = 0
    for record in records:
        if not record:
            continue
        dirty += 1
        # Porcelain v1 uses the first two bytes for XY (git-status manual).
        if b"R" in record[:2] or b"C" in record[:2]:
            next(records)
    refs = git("for-each-ref", "--format=%(refname)", "refs/remotes/").splitlines()
    log = git("log", "--all", "--not", "--remotes", "--format=%H %ct")
    old = {row.split()[0] for row in log.splitlines() if int(row.split()[1]) < cutoff}
    return {
        "dirty_count": dirty,
        "unpushed_old_count": len(old),
        "remote_ref_count": len(refs),
    }


def build_manifest(config, *, clock=None):
    validate(config)
    extensions, names = category_table(config)
    files, repositories = scan(config)
    for item in files:
        path = Path(item["path"])
        item["category"] = names.get(
            path.name.casefold(), extensions.get(path.suffix.casefold(), "unknown")
        )
    totals = aggregate(files)
    totals["categories"] = {
        category: aggregate([row for row in files if row["category"] == category])
        for category in sorted({row["category"] for row in files})
    }
    groups = {}
    for item in files:
        path = Path(item["path"])
        group = path.parts[0] if len(path.parts) > 1 else "."
        groups.setdefault(group, []).append(item)
    totals["top_level"] = {key: aggregate(rows) for key, rows in sorted(groups.items())}
    now = clock() if clock else datetime.now(UTC)
    if now.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    # Local age convention: one day; callers can override unpushed_hours.
    hours = config.get("unpushed_hours", 24)
    if type(hours) not in (int, float) or hours < 0:
        raise ValueError("unpushed_hours must be a finite nonnegative number")
    try:
        if not math.isfinite(hours):
            raise ValueError("nonfinite age")
        cutoff = (now - timedelta(hours=hours)).timestamp()
    except (OverflowError, ValueError) as error:
        raise ValueError("unpushed_hours exceeds datetime range") from error
    root = Path(config["root"]).resolve()
    states = []
    for path in repositories:
        label = (
            path.relative_to(root).as_posix()
            if path.is_relative_to(root)
            else path.as_posix()
        )
        states.append({"path": label, **repository_state(path, cutoff)})
    return {
        "schema": SCHEMA,
        "root": config["root"],
        "generated_utc": now.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "files": files,
        "totals": totals,
        "repos": sorted(states, key=lambda row: row["path"]),
    }


def main(argv=None, *, clock=None):
    # README Exit codes defines threshold=1 and invalid/incomplete inventory=2.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fail-above", type=int)
    args = parser.parse_args(argv)
    try:
        if args.fail_above is not None and args.fail_above < 0:
            raise ValueError("fail-above must be nonnegative")
        if (
            is_link(args.out)
            or args.out.resolve() == args.config.resolve()
            or (args.out.exists() and args.out.samefile(args.config))
        ):
            raise ValueError("out must not be a symlink or the configuration file")
        with args.config.open(encoding="utf-8") as stream:
            config = json.load(stream)
        validate(config)
        manifest = build_manifest(config, clock=clock)
        rendered = (
            json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
        )
        args.out.write_text(rendered, encoding="utf-8", newline="\n")
    except json.JSONDecodeError:
        print("error: invalid configuration JSON", file=sys.stderr)
        return 2
    except (TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (OSError, RuntimeError):
        print(
            "error: filesystem or Git access failed; no complete inventory",
            file=sys.stderr,
        )
        return 2
    totals = manifest["totals"]
    print(
        f"stray_files={totals['count']} bytes={totals['bytes']} "
        f"repositories={len(manifest['repos'])}"
    )
    return int(args.fail_above is not None and totals["count"] > args.fail_above)


if __name__ == "__main__":
    raise SystemExit(main())
