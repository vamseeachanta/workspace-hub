#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Manifest-driven, ff-only repository maintenance; no reset, deletion or push.

Source: Git 2.43.0 git-merge, --ff-only; git-fetch, explicit refspecs.
Policy limits and timeouts are required inputs; no engineering coefficients apply.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

STATUSES = {"synced", "dirty", "wedged", "busy", "wrong_branch", "missing", "fetch_failed", "error"}
ID = re.compile(r"[a-z][a-z0-9-]*\Z")
# Git object formats: SHA-1 and SHA-256; git rev-parse documentation, --show-object-format.
SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def number(value, *, positive=False):
    return (type(value) in (int, float) and math.isfinite(value)
            and (value > 0 if positive else value >= 0))


def timestamp(value):
    if not isinstance(value, str):
        raise TypeError("invalid timestamp")
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError("timezone required")
    return result


def public_status(data):
    """Allowlist projection: never serialize paths, remote URLs or Git diagnostics."""
    try:
        if data["schema_version"] != 1 or type(data["schema_version"]) is not int:
            return None
        timestamp(data["observed_at"])
        if not number(data["max_age_seconds"], positive=True) or not data["repos"]:
            return None
        rows = []
        seen = set()
        for row in data["repos"]:
            if not ID.fullmatch(row["id"]) or row["id"] in seen or row["status"] not in STATUSES:
                return None
            seen.add(row["id"])
            if type(row["dirty"]) is not bool or type(row["wedged"]) is not bool:
                return None
            if row["dirty"] != (row["status"] == "dirty") or row["wedged"] != (row["status"] == "wedged"):
                return None
            if row["head"] is not None and not SHA.fullmatch(row["head"]):
                return None
            if (row["last_success_at"] is not None and
                    timestamp(row["last_success_at"]) > timestamp(data["observed_at"])):
                return None
            if row["status"] == "synced" and (row["head"] is None or row["last_success_at"] is None):
                return None
            rows.append({k: row[k] for k in ("id", "status", "dirty", "wedged", "head", "last_success_at")})
        cleanup = data["cleanup"]
        if cleanup["status"] not in {"not_evaluated", "clear", "attention", "error"}:
            return None
        if not all(type(cleanup[k]) is int and cleanup[k] >= 0 for k in ("bytes", "expired_files")):
            return None
        return {"schema_version": 1, "observed_at": data["observed_at"],
                "max_age_seconds": data["max_age_seconds"], "repos": rows,
                "cleanup": {k: cleanup[k] for k in ("status", "bytes", "expired_files")}}
    except (KeyError, ValueError, TypeError, OverflowError):
        return None


def verdict(data, now=None):
    data = public_status(data)
    if data is None:
        return "MISSING-EVIDENCE"
    now = now or datetime.now(UTC)
    age = (now - timestamp(data["observed_at"])).total_seconds()
    if age < 0 or age > data["max_age_seconds"]:
        return "HYGIENE-STALE"
    if any(row["wedged"] for row in data["repos"]):
        return "HYGIENE-WEDGED"
    if any(row["dirty"] for row in data["repos"]):
        return "HYGIENE-DIRTY"
    if any(row["status"] != "synced" for row in data["repos"]):
        return "HYGIENE-BLOCKED"
    if any(row["last_success_at"] is None or
           not 0 <= (now - timestamp(row["last_success_at"])).total_seconds() <= data["max_age_seconds"]
           for row in data["repos"]):
        return "HYGIENE-STALE"
    if data["cleanup"]["status"] in {"attention", "error"}:
        return "HYGIENE-RESIDUE"
    return "HYGIENE-OK"


def under(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("relative path required")
    path = (root / value).resolve()
    if path == root or root not in path.parents:
        raise ValueError("path outside configured root")
    return path


def load_manifest(path, root):
    import yaml
    try:
        policy = yaml.safe_load(path.read_text())
        if type(policy["schema_version"]) is not int or policy["schema_version"] != 1:
            raise ValueError("unsupported schema")
        for key in ("git_timeout_seconds", "max_age_seconds"):
            if not number(policy[key], positive=True):
                raise ValueError("positive policy input required")
        if not isinstance(policy["repos"], list) or not policy["repos"]:
            raise ValueError("repository list required")
        seen = set()
        paths = set()
        for row in policy["repos"]:
            if not ID.fullmatch(row["id"]) or row["id"] in seen:
                raise ValueError("unique public aliases required")
            seen.add(row["id"])
            repo = under(root, row["path"])
            if repo in paths:
                raise ValueError("duplicate checkout")
            paths.add(repo)
            under(root, row["activity_lock"])
            # Check the complete ref with Git as well before any fetch.
            if not isinstance(row["branch"], str) or row["branch"].startswith("-"):
                raise ValueError("invalid branch")
            result = subprocess.run(["git", "check-ref-format", "refs/heads/" + row["branch"]],
                                    capture_output=True, check=False, env=git_env(), timeout=policy["git_timeout_seconds"])
            if result.returncode:
                raise ValueError("invalid branch")
        if not isinstance(policy["scratch"], list):
            raise TypeError("scratch list required")
        for row in policy["scratch"]:
            under(root, row["path"])
            if type(row["max_bytes"]) is not int or row["max_bytes"] < 0:
                raise ValueError("nonnegative size input required")
            if not number(row["max_age_seconds"], positive=True):
                raise ValueError("positive age input required")
        return policy
    except (KeyError, TypeError, AttributeError, yaml.YAMLError) as exc:
        raise ValueError("invalid manifest") from exc


def git_env():
    # Explicit cwd alone cannot defeat inherited repository bindings or config injection.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_TERMINAL_PROMPT="0")
    return env


def git(repo, timeout, *args):
    return subprocess.run(["git", "-C", str(repo), *args], env=git_env(),
                          capture_output=True, text=True, timeout=timeout, check=True).stdout.strip()


@contextmanager
def locked(path):
    # Lock in common Git dir coordinates duplicate manifests and linked worktrees.
    # No lock file is removed: unlinking would allow concurrent locks on different inodes.
    import fcntl
    with path.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def sync_repo(root, entry, timeout, previous, now):
    row = {"id": entry["id"], "status": "error", "dirty": False, "wedged": False,
           "head": None, "last_success_at": previous.get("last_success_at")}
    repo = under(root, entry["path"])
    activity = under(root, entry["activity_lock"])
    if not (repo / ".git").exists():
        row["status"] = "missing"
        return row
    try:
        # Refuse nested directories that merely inherit a parent repository.
        if Path(git(repo, timeout, "rev-parse", "--show-toplevel")).resolve() != repo:
            return row
        common = Path(git(repo, timeout, "rev-parse", "--git-common-dir"))
        if not common.is_absolute():
            common = repo / common
        with locked(common / "repo-hygiene.lock"):
            row["head"] = git(repo, timeout, "rev-parse", "HEAD")
            if activity.exists():
                row["status"] = "busy"
                return row
            try:
                branch = git(repo, timeout, "symbolic-ref", "--quiet", "--short", "HEAD")
            except subprocess.CalledProcessError:
                branch = None
            if branch != entry["branch"]:
                row["status"] = "wrong_branch"
                return row
            if git(repo, timeout, "status", "--porcelain=v1", "--untracked-files=all"):
                row.update(status="dirty", dirty=True)
                return row
            # Resolve a fetched object explicitly, avoiding upstream/pull/rebase configuration.
            try:
                git(repo, timeout, "fetch", "--no-tags", "origin", "refs/heads/" + entry["branch"])
            except (subprocess.SubprocessError, OSError):
                row["status"] = "fetch_failed"
                return row
            target = git(repo, timeout, "rev-parse", "FETCH_HEAD")
            try:
                git(repo, timeout, "merge-base", "--is-ancestor", row["head"], target)
            except subprocess.CalledProcessError as exc:
                if exc.returncode == 1:  # git merge-base --is-ancestor: false, not an execution error.
                    row.update(status="wedged", wedged=True)
                return row
            # Recheck after network latency; cooperating producers also hold the common lock.
            if activity.exists():
                row["status"] = "busy"
                return row
            if (git(repo, timeout, "status", "--porcelain=v1", "--untracked-files=all") or
                    git(repo, timeout, "rev-parse", "HEAD") != row["head"] or
                    git(repo, timeout, "symbolic-ref", "--quiet", "--short", "HEAD") != entry["branch"]):
                return row
            git(repo, timeout, "merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", "--no-edit", target)
            row["head"] = git(repo, timeout, "rev-parse", "HEAD")
            row.update(status="synced", last_success_at=now)
    except BlockingIOError:
        row["status"] = "busy"
    except (OSError, subprocess.SubprocessError):
        pass
    return row


def walk_error(error):
    raise error


def scratch_status(root, entries, now):
    result = {"status": "clear" if entries else "not_evaluated", "bytes": 0, "expired_files": 0}
    try:
        for entry in entries:
            path = under(root, entry["path"])
            if not path.is_dir():
                result["status"] = "error"
                continue
            total = 0
            for base, dirs, files in os.walk(path, followlinks=False, onerror=walk_error):
                dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
                for name in files:
                    item = Path(base) / name
                    if item.is_symlink():
                        continue
                    stat = item.stat()
                    total += stat.st_size
                    if now - stat.st_mtime > entry["max_age_seconds"]:
                        result["expired_files"] += 1
            result["bytes"] += total
            if (total > entry["max_bytes"] or result["expired_files"]) and result["status"] != "error":
                result["status"] = "attention"
    except OSError:
        result["status"] = "error"
    return result


def read_status(path):
    try:
        return public_status(json.loads(path.read_text()))
    except (OSError, ValueError):
        return None


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Same-directory atomic replacement: readers see complete old or new JSON after restart.
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".repo-sync-", delete=False) as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = handle.name
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attach-equality", action="store_true", help="merge public status into equality YAML from stdin")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--project", type=Path, help="emit allowlisted JSON only; no Git commands")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()
    if args.attach_equality:
        if not args.state or not args.output:
            parser.error("state and output are required")
        import yaml
        try:
            evidence = yaml.safe_load(sys.stdin.read())
            if not isinstance(evidence, dict) or not isinstance(evidence.get("dimensions"), dict):
                raise TypeError("invalid equality evidence")
            evidence["dimensions"]["repo_hygiene"] = read_status(args.state)
            atomic_write(args.output, yaml.safe_dump(evidence, sort_keys=False))
            return 0
        except (OSError, ValueError, TypeError, yaml.YAMLError):
            print("repo-sync: invalid equality evidence", file=sys.stderr)
            return 1
    if args.project:
        print(json.dumps(read_status(args.project)))
        return 0
    if not all((args.manifest, args.root, args.state)):
        parser.error("manifest, root and state are required")
    try:
        root = args.root.resolve(strict=True)
        policy = load_manifest(args.manifest, root)
        args.state.parent.mkdir(parents=True, exist_ok=True)
        with locked(args.state.with_suffix(args.state.suffix + ".lock")):
            previous = read_status(args.state) or {}
            prior = {r["id"]: r for r in previous.get("repos", [])}
            now = datetime.now(UTC)
            rows = [sync_repo(root, entry, policy["git_timeout_seconds"], prior.get(entry["id"], {}), now.isoformat())
                    for entry in policy["repos"]]
            data = {"schema_version": 1, "observed_at": now.isoformat(),
                    "max_age_seconds": policy["max_age_seconds"], "repos": rows,
                    "cleanup": scratch_status(root, policy["scratch"], now.timestamp())}
            atomic_write(args.state, json.dumps(data, sort_keys=True) + "\n")
            return 0 if verdict(data, now) == "HYGIENE-OK" else 1
    except BlockingIOError:
        print("repo-sync: already running", file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.SubprocessError):
        # Raw exceptions can contain private paths, command lines or credential-bearing URLs.
        print("repo-sync: configuration or operation failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
