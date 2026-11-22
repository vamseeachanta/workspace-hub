#!/usr/bin/env python3
"""Check current-index gitlinks against indexed .gitmodules without changing Git.

Git formats: git-ls-files --stage -z emits mode/object/stage TAB path NUL;
git-config --null --list emits key LF value NUL. See the Git manuals
for git-ls-files, git-config and index-format. Index mode 160000 is a gitlink;
100644 and 100755 are regular files; stage 0 denotes a resolved entry.
Exit statuses are defined in README-sync-ecosystem.md: clean, unmapped, error.
"""

import json
import os
import re
import subprocess
import sys


class DiagnosticError(Exception):
    """The index or its metadata cannot be interpreted reliably."""


def _quote(value: bytes) -> str:
    """Keep whitespace, control characters and undecodable path bytes unambiguous."""
    return json.dumps(os.fsdecode(value), ensure_ascii=True)


def _git(*args: str) -> subprocess.CompletedProcess:
    # Git's environment contract prevents implicit network/object substitution
    # and optional metadata writes; preserve the caller's selected index.
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0")
    # The root pathspec uses Git magic even when the caller requests literals.
    env["GIT_LITERAL_PATHSPECS"] = "0"
    try:
        return subprocess.run(["git", *args], env=env, capture_output=True, check=False)
    except OSError as error:
        # Do not echo Git stderr or executable paths from the environment.
        raise DiagnosticError("Git could not be executed") from error


def _index() -> tuple[set[bytes], bytes | None]:
    result = _git("ls-files", "--stage", "-z", "--full-name", "--", ":/")
    if result.returncode:
        raise DiagnosticError("Git could not read the current index")
    gitlinks = set()
    metadata_oid = None
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        header, separator, path = record.partition(b"\t")
        fields = header.split()
        if not separator or len(fields) != 3:
            raise DiagnosticError("Git returned an invalid index record")
        mode, oid, stage = fields
        if mode != b"160000" and path != b".gitmodules":
            continue
        if stage != b"0":
            raise DiagnosticError("Unmerged gitlink or indexed .gitmodules")
        if mode == b"160000":
            gitlinks.add(path)
        if path == b".gitmodules":
            if mode not in {b"100644", b"100755"}:
                raise DiagnosticError("Indexed .gitmodules must be a regular file")
            metadata_oid = oid
    return gitlinks, metadata_oid


def _declared_paths(oid: bytes | None) -> set[bytes]:
    if oid is None:
        return set()
    # Read the captured indexed object, never a working-tree file or an include.
    result = _git("config", "--no-includes", "--blob", oid.decode("ascii"),
                  "--null", "--list")
    if result.returncode:
        raise DiagnosticError("Git could not parse indexed .gitmodules")
    keys = set()
    paths = set()
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        key, separator, path = record.partition(b"\n")
        if not re.fullmatch(rb"submodule\..*\.path", key):
            continue
        if not separator or not path:
            raise DiagnosticError("Indexed .gitmodules contains an empty path declaration")
        if key in keys:
            raise DiagnosticError(f"Duplicate .gitmodules declaration: {_quote(key)}")
        if path in paths:
            raise DiagnosticError(f"Duplicate .gitmodules path: {_quote(path)}")
        keys.add(key)
        paths.add(path)
    return paths


def main() -> int:
    try:
        gitlinks, metadata_oid = _index()
        declared = _declared_paths(metadata_oid)
    except DiagnosticError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    unmapped = gitlinks - declared
    for path in sorted(unmapped):
        print(f"unmapped gitlink: {_quote(path)}")
    if unmapped:
        return 1
    print("OK: every indexed gitlink has a submodule path declaration")
    return 0


if __name__ == "__main__":
    sys.exit(main())
