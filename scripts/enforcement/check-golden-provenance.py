#!/usr/bin/env python3
"""Level 2 check: committed golden/baseline directories declare a comparator.

Policy source: .claude/rules/reproducibility-is-not-correctness.md (2026),
How to apply, comparator table; issue 3844 acceptance criteria. This validates
metadata declarations only, never the correctness of the declared evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

# Exact directory names and JSON filename are this check's discovery convention.
DIRECTORIES = frozenset({"golden", "goldens", "baseline", "baselines"})
CLASSES = frozenset({
    "closed-form", "measured", "cross-solver", "conservation", "archived-run", "none",
})
WARNING_CLASSES = frozenset({"archived-run", "none"})


def git(repo: Path, *args: str) -> bytes:
    """Read only from the explicit repository, independent of caller Git bindings."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(repo), *args], env=env,
        check=True, capture_output=True,
    ).stdout


def snapshot(repo: Path, ref: str) -> dict[str, tuple[str, str]]:
    """Pin one committed tree; preserve whitespace/newlines in tracked paths."""
    tree = git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{tree}}")
    records = git(repo, "ls-tree", "-r", "-z", tree.decode("ascii").strip())
    entries = {}
    for record in records.split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split()
        if kind in {"blob", "commit"}:
            entries[os.fsdecode(path)] = (mode, oid)
    return entries


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite JSON constant")


def audit(entries, read_blob) -> list[tuple[str, str, str]]:
    """Check every named directory using only records in the pinned Git tree."""
    directories = set()
    for path, (mode, _) in entries.items():
        parts = PurePosixPath(path).parts
        # Gitlinks represent directories even though ls-tree treats them as leaves.
        directory_parts = parts if mode == "160000" else parts[:-1]
        for index, part in enumerate(directory_parts):
            if part in DIRECTORIES:
                directories.add("/".join(parts[:index + 1]))

    findings = []
    for directory in sorted(directories):
        record = entries.get(f"{directory}/provenance.json")
        if record is None:
            findings.append(("ERROR", directory, "missing provenance.json"))
            continue
        mode, oid = record
        if mode not in {"100644", "100755"}:
            findings.append(("ERROR", directory, "provenance.json must be a regular Git blob"))
            continue
        try:
            payload = json.loads(
                read_blob(oid).decode("utf-8"),
                object_pairs_hook=unique_object, parse_constant=reject_constant,
            )
        except (ValueError, UnicodeError, RecursionError):
            findings.append(("ERROR", directory, "invalid provenance JSON"))
            continue
        comparator = payload.get("comparator") if isinstance(payload, dict) else None
        value = comparator.get("class") if isinstance(comparator, dict) else None
        if not isinstance(value, str) or value not in CLASSES:
            findings.append(("ERROR", directory, "missing or invalid comparator.class"))
        elif value in WARNING_CLASSES:
            findings.append(("WARNING", directory, "comparator does not establish correctness"))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository to inspect")
    parser.add_argument("--ref", default="HEAD", help="committed revision to inspect (default: HEAD)")
    args = parser.parse_args(argv)
    try:
        entries = snapshot(args.repo, args.ref)
        findings = audit(entries, lambda oid: git(args.repo, "cat-file", "blob", oid))
    except (OSError, subprocess.CalledProcessError):
        print("ERROR: unable to read the requested Git tree", file=sys.stderr)
        return 2  # CLI operational-error convention; not an engineering threshold.
    for severity, directory, message in findings:
        # JSON quoting keeps unusual tracked filenames on one diagnostic line.
        print(f"{severity}: {json.dumps(directory, ensure_ascii=True)}: {message}")
    errors = sum(severity == "ERROR" for severity, _, _ in findings)
    warnings = sum(severity == "WARNING" for severity, _, _ in findings)
    print(f"Golden provenance: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
