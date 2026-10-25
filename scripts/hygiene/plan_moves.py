"""Manifest-driven, reviewed moves. See PLAN_MOVES.md for the safety contract.

Protocol numbers (schema, rule indices and exit codes) follow issue #4221 and
PLAN_MOVES.md. There are no engineering coefficients or acceptance tolerances.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import hmac
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath

SCHEMA = 1  # Issue #4221, inventory manifest schema version 1.


class SafetyError(ValueError):
    """A refusal with a fixed message, safe to print without input payloads."""


def parse_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise SafetyError("duplicate JSON key")
            result[key] = value
        return result

    return json.loads(raw, object_pairs_hook=unique)


def read_json(path):
    return parse_json(Path(path).read_bytes())


def relative(value, *, directory=False):
    """Use portable POSIX paths and exclude repository control metadata."""
    if directory and value == ".":
        return value
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise SafetyError("expected a portable relative path")
    parts = value.split("/")
    # Reject case aliases of control metadata and trailing-dot/space aliases.
    if any(
        part in ("", ".", "..")
        or part.casefold() == ".git"
        or part.endswith((".", " "))
        for part in parts
    ):
        raise SafetyError("unsafe relative path")
    # Python 3.11 pathlib, PurePath.is_reserved: Windows device names are not
    # ordinary files, even when an inventory was prepared on another platform.
    # https://docs.python.org/3.11/library/pathlib.html#pathlib.PurePath.is_reserved
    if any(PureWindowsPath(part).is_reserved() for part in parts):
        raise SafetyError("reserved device name")
    if any(ord(char) < ord(" ") for char in value):
        raise SafetyError("control character in path")
    return value


def is_link(path):
    """Reject symlinks and Windows reparse points, including junctions."""
    try:
        info = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def checked_path(root, value, *, directory=False):
    relative(value, directory=directory)
    path = root if value == "." else root.joinpath(*value.split("/"))
    # Inspect even dangling symlinks; resolve() alone would hide their presence.
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if is_link(current):
            raise SafetyError("symlinks are not permitted")
    return path


def checked_root(value):
    root = Path(value)
    if (
        not root.is_absolute()
        or root.resolve() != root
        or not root.is_dir()
        or any(is_link(path) for path in (root, *root.parents))
    ):
        raise SafetyError(
            "root must be an existing absolute directory without symlinks"
        )
    return root


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def matches(path, pattern):
    if not isinstance(pattern, str) or not pattern:
        raise SafetyError("match must be a nonempty string")
    if any(char in pattern for char in "*?["):
        return fnmatch.fnmatchcase(path, pattern)
    prefix = pattern.rstrip("/")
    return path == prefix or path.startswith(prefix + "/")


def destination_problems(root, destination):
    problems = []
    if destination.exists():
        problems.append("destination exists")
    for parent in destination.parents:
        if parent == root:
            break
        if parent.exists() and not parent.is_dir():
            problems.append("destination parent is not a directory")
            break
    return problems


def repo_map(root, repos):
    result = {}
    for repo in repos:
        name, path = repo["name"], relative(repo["path"], directory=True)
        if not isinstance(name, str) or not name or name in result:
            raise SafetyError("repository names must be unique nonempty strings")
        if not checked_path(root, path, directory=True).is_dir():
            raise SafetyError("repository directory is missing")
        if path in result.values():
            raise SafetyError("repository paths must be unique")
        result[name] = path
    return result


def within(path, directory):
    return directory == "." or path == directory or path.startswith(directory + "/")


def summarize(entries, ignored=0):
    summary = {
        "repos": {},
        "bytes": 0,
        "conflicts": 0,
        "unmatched": 0,
        "ignored": ignored,
    }
    for entry in entries:
        summary["bytes"] += entry["size"]
        if entry["status"] == "unmatched":
            summary["unmatched"] += 1
        else:
            counts = summary["repos"].setdefault(
                entry["repo"], {"count": 0, "bytes": 0}
            )
            counts["count"] += 1
            counts["bytes"] += entry["size"]
        summary["conflicts"] += entry["status"] == "conflict"
    return summary


def build_plan(manifest, config):
    if type(manifest["schema"]) is not int or manifest["schema"] != SCHEMA:
        raise SafetyError("unsupported inventory schema")
    root = checked_root(manifest["root"])
    repos = repo_map(root, manifest["repos"])
    rules, ignore = config.get("rules", []), config.get("ignore", [])
    if not isinstance(rules, list) or not isinstance(ignore, list):
        raise SafetyError("rules and ignore must be lists")
    if any(not isinstance(pattern, str) or not pattern for pattern in ignore):
        raise SafetyError("ignore patterns must be nonempty strings")
    for rule in rules:
        matches("", rule["match"])
        relative(rule["dest"], directory=True)
        if rule["repo"] not in repos:
            raise SafetyError("rule names an unknown repository")
    default = config.get("default_repo")
    if default is not None and default not in repos:
        raise SafetyError("default names an unknown repository")
    entries, seen, ignored = [], set(), 0
    for item in manifest["files"]:
        source = relative(item["path"])
        if source in seen:
            raise SafetyError("duplicate source")
        seen.add(source)
        size = item["size"]
        if type(size) is not int or size < 0:
            raise SafetyError("size must be nonnegative integer bytes")
        if any(within(source, path) for path in repos.values()):
            raise SafetyError("inventory contains a file inside a repository")
        if any(fnmatch.fnmatchcase(source, pattern) for pattern in ignore):
            ignored += 1
            continue
        path = checked_path(root, source)
        entry = {
            "source": source,
            "size": size,
            "repo": None,
            "dest": None,
            "reason": None,
            "status": "unmatched",
        }
        for index, rule in enumerate(rules):
            if matches(source, rule["match"]):
                entry.update(repo=rule["repo"], reason=index)
                directory = rule["dest"]
                break
        else:
            directory = "."
            if default is not None:
                entry.update(repo=default, reason="default_repo")
        if entry["repo"] is not None:
            entry["dest"] = str(
                PurePosixPath(repos[entry["repo"]]) / directory / path.name
            )
            destination = checked_path(root, entry["dest"])
            problems = destination_problems(root, destination)
            if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
                problems.append("source is not a regular file")
            elif path.stat().st_size != size:
                problems.append("source size differs from inventory")
            else:
                entry["sha256"] = digest(path)
            entry.update(status="conflict" if problems else "ready", conflicts=problems)
        entries.append(entry)
    targets = {}
    for entry in entries:
        if entry["dest"] is not None:
            targets.setdefault(entry["dest"], []).append(entry)
    for group in targets.values():
        if len(group) > 1:
            for entry in group:
                entry["status"] = "conflict"
                entry["conflicts"].append("multiple sources share destination")
    for destination, group in targets.items():
        for parent in PurePosixPath(destination).parents:
            if str(parent) in targets:
                for entry in group + targets[str(parent)]:
                    entry["status"] = "conflict"
                    entry["conflicts"].append(
                        "a destination is another destination's parent"
                    )
    return {
        "schema": SCHEMA,
        "kind": "moves",
        "root": str(root),
        "repos": manifest["repos"],
        "entries": entries,
        "summary": summarize(entries, ignored),
    }


def print_summary(summary):
    for name, counts in sorted(summary["repos"].items()):
        print(f"{name}: {counts['count']} files, {counts['bytes']} bytes")
    print(
        f"Total: {summary['bytes']} bytes; conflicts: {summary['conflicts']}; "
        f"unmatched: {summary['unmatched']}; ignored: {summary['ignored']}"
    )


def write_plan(plan, out, protected=()):
    output = Path(out)
    root = Path(plan["root"])
    paths = {Path(p).resolve() for p in protected}
    for entry in plan["entries"]:
        paths.add(root / entry["source"])
        if entry["dest"] is not None:
            paths.add(root / entry["dest"])
    if output.resolve() in paths:
        raise SafetyError("output would replace an input or move endpoint")
    # Exclusive creation avoids overwriting unrelated files, including symlinks.
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(plan, stream, indent=2, sort_keys=True)
        stream.write("\n")


def utc_now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def verify_file(path, entry):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size != entry["size"]:
        raise SafetyError("file type or size differs from reviewed plan")
    if digest(path) != entry["sha256"]:
        raise SafetyError("file digest differs from reviewed plan")
    after = path.lstat()
    if (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ):
        raise SafetyError("file changed during verification")


def copy_stream(source, destination):
    # Python 3.11 shutil.copyfileobj: default chunking bounds memory use.
    # https://docs.python.org/3.11/library/shutil.html#shutil.copyfileobj
    shutil.copyfileobj(source, destination)


def remove_verified_source(root, entry):
    # Recheck both endpoints immediately before removing the original name.
    source = checked_path(root, entry["source"])
    destination = checked_path(root, entry["dest"])
    verify_file(destination, entry)
    if source.exists():
        verify_file(source, entry)
        source.unlink()


def append_event(log, event):
    with Path(log).open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell():
            stream.seek(-1, os.SEEK_END)
            if stream.read(1) != b"\n":
                raise SafetyError("log is missing its final newline")
        stream.write((json.dumps(event, sort_keys=True) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())


def read_events(log):
    path = Path(log)
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise SafetyError("log must be a regular file")
    # Refuse an unterminated record before any append or filesystem mutation.
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise SafetyError("log is missing its final newline")
    return [parse_json(line.decode("utf-8")) for line in raw.split(b"\n")[:-1]]


def git_run(repo, args):
    # Fixture and caller bindings must not redirect commands to another checkout.
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    # Git add documentation, pathspec: treat names as literals, including '*'.
    # https://git-scm.com/docs/git-add
    env["GIT_LITERAL_PATHSPECS"] = "1"
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, env=env
    ).stdout


def stage_target(root, repos, entry):
    repo = checked_path(root, repos[entry["repo"]], directory=True)
    top = Path(os.fsdecode(git_run(repo, ["rev-parse", "--show-toplevel"])).strip())
    if top.resolve() != repo:
        raise SafetyError("destination is not the declared repository root")
    relative_path = (root / entry["dest"]).relative_to(repo).as_posix()
    attributes = git_run(
        repo, ["check-attr", "-z", "filter", "--", relative_path]
    ).split(b"\0")
    # git-check-attr OUTPUT: path, attribute, value, each NUL-terminated with -z.
    # https://git-scm.com/docs/git-check-attr#_output
    try:
        attr_path, attr_name, attr_value, terminator = attributes
    except ValueError:
        raise SafetyError("unexpected Git attribute response") from None
    if (attr_path, attr_name, terminator) != (
        os.fsencode(relative_path),
        b"filter",
        b"",
    ):
        raise SafetyError("unexpected Git attribute response")
    if attr_value == b"lfs":
        raise SafetyError("LFS staging is prohibited")
    return repo, relative_path


def validate_plan(plan):
    if type(plan["schema"]) is not int or plan["schema"] != SCHEMA:
        raise SafetyError("unsupported plan schema")
    if plan["kind"] not in {"moves", "undo"}:
        raise SafetyError("unsupported plan kind")
    root = checked_root(plan["root"])
    repos = repo_map(root, plan["repos"])
    sources, destinations = set(), set()
    for entry in plan["entries"]:
        source = relative(entry["source"])
        checked_path(root, source)
        if source in sources:
            raise SafetyError("duplicate source")
        sources.add(source)
        if type(entry["size"]) is not int or entry["size"] < 0:
            raise SafetyError("invalid size")
        if entry["status"] == "unmatched":
            if entry["dest"] is not None or entry["repo"] is not None:
                raise SafetyError("unmatched entry has a destination")
            continue
        if entry["status"] != "ready" or entry.get("conflicts"):
            raise SafetyError("conflicts must be resolved in a new reviewed plan")
        destination = relative(entry["dest"])
        checked_path(root, destination)
        if entry["repo"] not in repos:
            raise SafetyError("unknown repository")
        repo = repos[entry["repo"]]
        inside, outside = (
            (destination, source) if plan["kind"] == "moves" else (source, destination)
        )
        if not within(inside, repo) or any(
            within(outside, path) for path in repos.values()
        ):
            raise SafetyError("move does not cross the declared repository boundary")
        expected = entry["sha256"]
        # hashlib's SHA-256 hexdigest determines length, not a tolerance.
        if not isinstance(expected, str) or len(expected) != len(
            hashlib.sha256().hexdigest()
        ):
            raise SafetyError("invalid content digest")
        if any(char not in "0123456789abcdef" for char in expected):
            raise SafetyError("invalid content digest")
        if destination in destinations:
            raise SafetyError("duplicate destination")
        destinations.add(destination)
    if sources & destinations:
        raise SafetyError("source and destination sets overlap")
    if any(
        str(parent) in destinations
        for path in destinations
        for parent in PurePosixPath(path).parents
    ):
        raise SafetyError("a destination is another destination's parent")
    return root, repos


def apply_plan(plan_path, log, confirm, *, git_add=False, clock=utc_now):
    # Parse the exact bytes whose digest was confirmed, without reopening them.
    raw = Path(plan_path).read_bytes()
    plan_hash = hashlib.sha256(raw).hexdigest()
    if not isinstance(confirm, str) or not hmac.compare_digest(plan_hash, confirm):
        raise SafetyError("confirmation does not match plan bytes")
    plan = parse_json(raw)
    root, repos = validate_plan(plan)
    if git_add and plan["kind"] == "undo":
        raise SafetyError("undo does not stage repository changes")
    endpoints = {
        root / entry[key]
        for entry in plan["entries"]
        for key in ("source", "dest")
        if entry[key] is not None
    }
    log = Path(log).absolute()
    if log.resolve() != log or log in endpoints or log == Path(plan_path).resolve():
        raise SafetyError("log aliases a protected path or symlink")
    if log.exists() and any(
        path.exists() and log.samefile(path) for path in endpoints | {Path(plan_path)}
    ):
        raise SafetyError("log is a hardlink to a protected file")
    if root in log.parents and any(
        part.casefold() == ".git" for part in log.relative_to(root).parts
    ):
        raise SafetyError("log cannot modify Git metadata")
    history = read_events(log)
    records = {}
    for event in history:
        if event["plan_sha256"] != plan_hash:
            raise SafetyError("log belongs to another plan")
        key = (event["source"], event["destination"], event["hash"])
        records.setdefault(key, set()).add(event["result"])
    # Check all completed receipts and staging eligibility before any mutation.
    work = []
    for entry in plan["entries"]:
        if entry["status"] == "unmatched":
            continue
        source, destination = (
            checked_path(root, entry["source"]),
            checked_path(root, entry["dest"]),
        )
        prior = records.get((entry["source"], entry["dest"], entry["sha256"]), set())
        if "done" in prior:
            verify_file(destination, entry)
            if source.exists():
                raise SafetyError("completed source was recreated")
        elif "copied" in prior:
            verify_file(destination, entry)
            if source.exists():
                verify_file(source, entry)
        else:
            verify_file(source, entry)
            if destination_problems(root, destination):
                raise SafetyError(
                    "destination or its parents block the move without copied receipt"
                )
        staging = stage_target(root, repos, entry) if git_add else None
        work.append((entry, prior, staging))
    for entry, prior, staging in work:

        def record(result, entry=entry, **extra):
            append_event(
                log,
                {
                    "time": clock(),
                    "root": str(root),
                    "repos": plan["repos"],
                    "plan_sha256": plan_hash,
                    "source": entry["source"],
                    "destination": entry["dest"],
                    "hash": entry["sha256"],
                    "size": entry["size"],
                    "repo": entry["repo"],
                    "result": result,
                    **extra,
                },
            )

        try:
            if "done" not in prior:
                if "copied" not in prior:
                    source = checked_path(root, entry["source"])
                    destination = checked_path(root, entry["dest"])
                    verify_file(source, entry)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    checked_path(root, entry["dest"])
                    with source.open("rb") as src, destination.open("xb") as dst:
                        copy_stream(src, dst)
                        dst.flush()
                        os.fsync(dst.fileno())
                    verify_file(destination, entry)
                    verify_file(source, entry)
                    record("copied")
                remove_verified_source(root, entry)
                record("done")
            if staging and "staged" not in prior:
                # Recheck attributes just before staging, as well as before moves.
                repo, path = stage_target(root, repos, entry)
                git_run(repo, ["add", "--", path])
                record("staged", staged_paths=[path])
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            record("error", error=type(error).__name__)
            raise
    return plan


def build_undo(log):
    history = read_events(log)
    if not history:
        raise SafetyError("log has no completed moves")
    first = history[0]
    entries, seen = [], set()
    for event in reversed(history):
        if any(event[key] != first[key] for key in ("root", "repos", "plan_sha256")):
            raise SafetyError("mixed log context")
        key = (event["source"], event["destination"])
        if event["result"] != "done" or key in seen:
            continue
        seen.add(key)
        entries.append(
            {
                "source": event["destination"],
                "dest": event["source"],
                "size": event["size"],
                "sha256": event["hash"],
                "repo": event["repo"],
                "reason": "undo",
                "status": "ready",
                "conflicts": [],
            }
        )
    if not entries:
        raise SafetyError("log has no completed moves")
    plan = {
        "schema": SCHEMA,
        "kind": "undo",
        "root": first["root"],
        "repos": first["repos"],
        "entries": entries,
        "summary": summarize(entries),
    }
    validate_plan(plan)
    root = Path(plan["root"])
    for entry in entries:
        problems = destination_problems(root, checked_path(root, entry["dest"]))
        try:
            verify_file(checked_path(root, entry["source"]), entry)
        except (OSError, ValueError):
            problems.append("reverse source differs from completed receipt")
        entry.update(status="conflict" if problems else "ready", conflicts=problems)
    plan["summary"] = summarize(entries)
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--manifest")
    mode.add_argument("--apply")
    mode.add_argument("--undo-from-log")
    parser.add_argument("--config")
    parser.add_argument("--out")
    parser.add_argument("--log")
    parser.add_argument("--confirm")
    parser.add_argument("--git-add", action="store_true")
    args = parser.parse_args(argv)
    if args.apply:
        if not args.log or not args.confirm or args.config or args.out:
            parser.error(
                "apply requires log and confirm; config and out are not permitted"
            )
    elif not args.out or args.log or args.confirm or args.git_add:
        parser.error("planning requires out; log, confirm and git-add are apply-only")
    elif bool(args.manifest) != bool(args.config):
        parser.error("manifest planning requires config; undo does not use config")
    try:
        if args.apply:
            plan = apply_plan(args.apply, args.log, args.confirm, git_add=args.git_add)
        elif args.undo_from_log:
            plan = build_undo(args.undo_from_log)
            write_plan(plan, args.out, (args.undo_from_log,))
        else:
            plan = build_plan(read_json(args.manifest), read_json(args.config))
            write_plan(plan, args.out, (args.manifest, args.config))
        print_summary(plan["summary"])
        return 0
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        # Only intentional fixed messages are printed; OS/JSON/Git errors may
        # contain private paths or payloads and are reported by class alone.
        detail = str(error) if isinstance(error, SafetyError) else type(error).__name__
        print(f"Refused: {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
