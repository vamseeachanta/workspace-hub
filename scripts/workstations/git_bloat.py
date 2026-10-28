"""Read-only Git bloat evidence, with no cleanup or history-rewrite verdict.

Sources: Git manuals gitrepository-layout (commondir, objects/info/alternates),
git-rev-list (--disk-usage, --all), git-ls-tree (-r, -z), consulted 2026-10-22.
Byte totals are sums of measured file metadata, not reclamation estimates.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Importing the local metadata helper must not write bytecode to the checkout.
sys.dont_write_bytecode = True
from repo_footprint import _git_dirs, _Scanner


def _unknown(reason: str) -> dict:
    return {"status": "NOT_EVALUATED", "reason": reason}


def storage_observation(common: Path) -> dict:
    """Reuse the footprint scanner's no-follow, hardlink-deduplicated accounting."""
    scanner = _Scanner()
    total = scanner.scan(common, git=True)["git"]
    categories = scanner.git_breakdown
    complete = not scanner.issues
    # Lower bounds must not be presented as complete measurements on read errors.
    if not complete:
        for measured in (total, *categories.values()):
            measured["logical_bytes"] = None
            measured["allocated_bytes"] = None
    return {
        "status": "EVALUATED" if complete else "NOT_EVALUATED",
        "scope": "common_git_directory",
        "logical_file_bytes": total["logical_bytes"],
        "allocated_file_bytes": total["allocated_bytes"],
        "non_object_logical_file_bytes": (
            sum(value["logical_bytes"] for key, value in categories.items() if key != "objects")
            if complete else None
        ),
        "categories": categories,
        "issue_codes": sorted({issue["code"] for issue in scanner.issues}),
    }


def _git(repo: Path, args: list[str], timeout_seconds: int, *, optional: bool = False) -> bytes:
    # Caller repository bindings must not redirect observation to another checkout.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1",
               GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "protocol.allow=never",
         "-c", "core.fsmonitor=false", "-C", str(repo), *args],
        capture_output=True, env=env, timeout=timeout_seconds, check=False,
    )
    if result.returncode and not (optional and result.returncode == 1):
        # Git stderr can contain private locations or remote credential material.
        raise ValueError("git_observation_failed")
    return result.stdout if not result.returncode else b""


def _snapshot(repo: Path, timeout_seconds: int) -> tuple[bytes, bytes, bytes]:
    return (
        _git(repo, ["rev-parse", "--verify", "HEAD"], timeout_seconds).strip(),
        _git(repo, ["for-each-ref", "--format=%(refname) %(objectname)"], timeout_seconds),
        # Git ls-files manual, --stage: include mode, object ID and conflict stage
        # so content-only index changes invalidate the same observation too.
        # --full-name keeps root-relative output; :/ also selects the whole index.
        _git(repo, ["ls-files", "--stage", "--full-name", "-z", "--", ":/"], timeout_seconds),
    )


def _candidate(value: str) -> str:
    # Literal repo-relative paths only: filter patterns are outside this contract.
    path = value.removesuffix("/")
    # Only ASCII letters introduce Windows drives; pathlib differs by version.
    drive = len(path) >= 2 and path[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" and path[1] == ":"
    if (not path or path.startswith("/") or drive or "\\" in path
            or any(part in {"", ".", ".."} for part in path.split("/"))
            or any(ord(char) < 32 or char in "*?[]" for char in path)):
        raise ValueError("invalid_candidate_path")
    return path


def _live_paths(repo: Path, snapshot: tuple, timeout_seconds: int) -> set[bytes]:
    head, refs, index = snapshot
    tips = {head, *(line.rsplit(b" ", 1)[-1] for line in refs.splitlines())}
    paths = {entry.split(b"\t", 1)[-1] for entry in index.split(b"\0")}
    for tip in sorted(tips):
        # Git ls-tree manual: -z provides unquoted NUL-separated pathnames;
        # -t retains directory entries, including explicitly stored empty trees.
        paths.update(_git(repo, ["ls-tree", "-rtz", "--name-only", "--full-tree",
                                 tip.decode("ascii")], timeout_seconds).split(b"\0"))
    paths.discard(b"")
    return paths


def inspect(
    repo: Path, *, timeout_seconds: int, reachable: bool = False,
    candidates: list[str] | tuple[str, ...] = (),
) -> dict:
    """Observe local storage and explicit candidates; never mutate the repository.

    Timeout is a caller-supplied operational bound for each Git subprocess.
    NOT_EVALUATED is evidence status, not a recommendation for maintenance.
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    result = {
        "status": "EVALUATED",
        "storage": _unknown("repository_unavailable"),
        "reachable": {**_unknown("not_requested"), "disk_bytes": None},
        "candidates": [],
        "reclaimable_bytes": _unknown("requires_authorized_rehearsal_and_retention_review"),
        "issue_codes": [],
    }
    for value in candidates:
        try:
            path = _candidate(value)
            result["candidates"].append({"path": path, **_unknown("inspection_pending")})
        except ValueError:
            # Do not reflect malformed control characters or absolute paths.
            result["candidates"].append(_unknown("invalid_candidate_path"))
    try:
        _, common = _git_dirs(Path(repo))
        if not common.is_dir():
            raise ValueError("repository_unavailable")
        before = _snapshot(repo, timeout_seconds)
        result["storage"] = storage_observation(common)
        incomplete = result["storage"]["status"] != "EVALUATED"
        shallow = _git(repo, ["rev-parse", "--is-shallow-repository"], timeout_seconds).strip()
        promisor = _git(repo, ["config", "--get-regexp", r"^remote\..*\.promisor$"],
                        timeout_seconds, optional=True)
        partial = _git(repo, ["config", "--get", "extensions.partialclone"],
                       timeout_seconds, optional=True)
        # A promisor marker remains relevant even if its remote was removed.
        promisor_pack = any((common / "objects/pack").glob("*.promisor"))
        incomplete |= shallow != b"false" or bool(promisor or partial or promisor_pack)
        if incomplete:
            result["issue_codes"].append("incomplete_local_evidence")
            if reachable:
                result["reachable"]["reason"] = "incomplete_local_evidence"
            for row in result["candidates"]:
                if "path" in row:
                    row["reason"] = "incomplete_local_evidence"
        else:
            if any("path" in row for row in result["candidates"]):
                live = _live_paths(repo, before, timeout_seconds)
                for row in result["candidates"]:
                    if "path" not in row:
                        continue
                    path = os.fsencode(row["path"])
                    blocked = any(value == path or value.startswith(path + b"/") for value in live)
                    row.update(status="BLOCKED_LIVE_PATH" if blocked else "ABSENT_FROM_TIPS")
                    row.pop("reason", None)
            if reachable:
                raw = _git(repo, ["rev-list", "--disk-usage", "--objects", "--all"], timeout_seconds).strip()
                if not raw.isdigit():
                    raise ValueError("invalid_reachable_measurement")
                result["reachable"] = {"status": "EVALUATED", "disk_bytes": int(raw),
                                       "scope": "all_refs_and_head_excluding_reflog_only_objects"}
        if before != _snapshot(repo, timeout_seconds):
            raise ValueError("refs_or_index_changed")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exception:
        # Fail closed without printing exception text, locations or Git stderr.
        reason = "git_or_storage_observation_failed"
        if isinstance(exception, ValueError) and str(exception) == "refs_or_index_changed":
            reason = "refs_or_index_changed"
        result["issue_codes"].append(reason)
        if reachable:
            result["reachable"] = {**_unknown(reason), "disk_bytes": None}
        for row in result["candidates"]:
            if "path" in row:
                row.update(_unknown(reason))
    if (result["storage"]["status"] != "EVALUATED" or result["issue_codes"]
            or (reachable and result["reachable"]["status"] != "EVALUATED")
            or any(row["status"] == "NOT_EVALUATED" for row in result["candidates"])):
        result["status"] = "NOT_EVALUATED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--reachable", action="store_true")
    parser.add_argument("--candidate", action="append", default=[])
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    report = inspect(args.repo, timeout_seconds=args.timeout_seconds,
                     reachable=args.reachable, candidates=args.candidate)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report["status"] == "EVALUATED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
