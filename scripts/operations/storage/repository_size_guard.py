#!/usr/bin/env python3
"""Check logical Git tree bytes against explicit policy inputs; never alter Git.

Basis: storage guard G1 in issue #4085. No acceptance limits are inferred from
its ambiguous MB unit: every byte cap is a required policy input instead.
Git git-ls-tree(1), version 2.42.0, Output Format documents -l sizes in bytes
and -z verbatim, NUL-terminated paths:
https://git-scm.com/docs/git-ls-tree/2.42.0#_output_format
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


class NotEvaluated(ValueError):
    """The required criterion or measurement is unavailable."""


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise NotEvaluated("duplicate policy key")
        result[key] = value
    return result


def _byte_limit(value):
    # Zero denotes an explicit empty-content budget, not an unknown criterion.
    if type(value) is not int or value < 0:
        raise NotEvaluated("byte limits must be nonnegative integers")


def load_policy(path: Path) -> dict:
    """Read required caps and exact-path exceptions; reject ambiguous policies."""
    try:
        policy = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
    except NotEvaluated:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise NotEvaluated("policy unreadable or invalid JSON") from exc
    if not isinstance(policy, dict) or set(policy) != {
        "max_total_bytes", "max_file_bytes", "exceptions",
    }:
        raise NotEvaluated("policy requires total cap, file cap and exceptions")
    _byte_limit(policy["max_total_bytes"])
    _byte_limit(policy["max_file_bytes"])
    if not isinstance(policy["exceptions"], dict):
        raise NotEvaluated("exceptions must map exact relative paths to byte caps")
    for name, cap in policy["exceptions"].items():
        if (
            not name or name.startswith("/") or "\\" in name or "\0" in name
            or any(part in {"", ".", ".."} for part in name.split("/"))
        ):
            raise NotEvaluated("exception path must be canonical and relative")
        _byte_limit(cap)
    return policy


def parse_tree(raw: bytes) -> dict[str, int]:
    """Read the cited -rlz format without splitting paths on whitespace."""
    if raw and not raw.endswith(b"\0"):
        raise NotEvaluated("incomplete Git tree output")
    entries = {}
    for record in raw.split(b"\0")[:-1]:
        try:
            metadata, name = record.split(b"\t", 1)
            _mode, kind, _oid, size = metadata.split()
            if kind != b"blob":
                raise NotEvaluated("non-blob content requires separate measurement")
            if not size.isdigit() or not name:
                raise NotEvaluated("invalid Git blob size or path")
            path = os.fsdecode(name)
            if path in entries:
                raise NotEvaluated("duplicate Git tree path")
            entries[path] = int(size)
        except ValueError as exc:
            if isinstance(exc, NotEvaluated):
                raise
            raise NotEvaluated("invalid Git tree output") from exc
    return entries


def git_environment() -> dict[str, str]:
    """Isolate repository selection and prevent lazy fetching in partial clones."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    # git(1), version 2.42.0, Environment Variables: an empty protocol list
    # denies all transport, including versions predating GIT_NO_LAZY_FETCH.
    # https://raw.githubusercontent.com/git/git/v2.42.0/Documentation/git.txt
    env["GIT_ALLOW_PROTOCOL"] = ""
    return env


def inspect_tree(repo: Path, revision: str) -> dict[str, int]:
    """Resolve once to an immutable tree, then enumerate its logical blob sizes."""
    def git(*args):
        try:
            return subprocess.run(
                ["git", "--no-replace-objects", "-C", str(repo), *args],
                env=git_environment(), check=True, capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            # Git stderr may contain private local paths or remote addresses.
            raise NotEvaluated("Git tree unavailable") from exc

    tree = git("rev-parse", "--verify", "--end-of-options", f"{revision}^{{tree}}")
    return parse_tree(git("ls-tree", "-r", "-l", "-z", "--full-tree", tree.decode().strip()))


def evaluate(entries: dict[str, int], policy: dict) -> dict:
    """Sum per-path bytes; compare unrounded integers with caller-provided caps."""
    total = sum(entries.values())
    violations = []
    for path, size in sorted(entries.items()):
        cap = policy["exceptions"].get(path, policy["max_file_bytes"])
        if size > cap:
            violations.append({"path": path, "size_bytes": size, "limit_bytes": cap})
    total_exceeded = total > policy["max_total_bytes"]
    return {
        "status": "BLOCK" if total_exceeded or violations else "PASS",
        "total_bytes": total, "max_total_bytes": policy["max_total_bytes"],
        "file_count": len(entries), "total_exceeded": total_exceeded,
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy)
        result = evaluate(inspect_tree(args.repo, args.revision), policy)
    except NotEvaluated as exc:
        print(json.dumps({"status": "NOT_EVALUATED", "reason": str(exc)}))
        return 2  # CLI protocol: see repository-size-guard.md, Exit status.
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
