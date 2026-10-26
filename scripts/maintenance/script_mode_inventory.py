"""Read indexed modes and shebang candidates without modifying a repository.

Git's index is authoritative, including when working-tree permissions differ.
Every indexed path is reported; a script_candidate flag means only that a
regular indexed blob starts with a shebang. It is a maintainer review candidate,
not a finding that its mode is defective. Sourced libraries need not execute.

Format and stage basis: https://git-scm.com/docs/git-ls-files (OUTPUT, --stage,
-z, --full-name). Mode basis: https://git-scm.com/docs/git-fast-import
(filemodify: 100644 and 100755 are regular files; 120000 is a symlink;
160000 is a gitlink). Symlinks and gitlinks are reported without following them.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess


REGULAR_MODES = {b"100644", b"100755"}


class InventoryError(Exception):
    """The index cannot provide an unambiguous inventory."""


def _git(repository, *args):
    # An explicit repository must not inherit another caller's index or objects.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1"
    )
    try:
        return subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "-C", str(repository), *args],
            capture_output=True,
            check=True,
            env=env,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        # Do not echo unrelated Git diagnostics or absolute repository paths.
        raise InventoryError("cannot read Git index or indexed blob") from exc


def inventory(repository):
    """Return deterministic records from the explicitly supplied repository.

    Paths are relative to its root, even for a subdirectory argument. The NUL
    separator preserves newlines; only the first TAB separates metadata from
    path bytes. JSON escapes unusual characters, including non-UTF-8 path bytes.
    No working-tree file contents or permissions are consulted.
    """
    repository = Path(repository).resolve()
    raw = _git(repository, "ls-files", "--stage", "--full-name", "-z", "--", ":/")
    entries = []
    unmerged = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", maxsplit=1)
        mode, oid, stage = metadata.split()
        # git-ls-files OUTPUT documents higher stages for unmerged entries.
        if stage != b"0":
            unmerged.add(path)
        entries.append((path, mode, oid))

    if unmerged:
        paths = json.dumps([os.fsdecode(path) for path in sorted(unmerged)])
        raise InventoryError(f"unmerged index entries: {paths}; resolve before inventory")

    results = []
    for path, mode, oid in sorted(entries):
        candidate = False
        if mode in REGULAR_MODES:
            candidate = _git(repository, "cat-file", "blob", oid.decode("ascii")).startswith(b"#!")
        results.append({
            "path": os.fsdecode(path),
            "indexed_mode": mode.decode("ascii"),
            "script_candidate": candidate,
        })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Read-only indexed script mode inventory for maintainer review. "
        "Shebang candidates are not automatic mode defects."
    )
    parser.add_argument("repository", type=Path, help="explicit Git repository to inventory")
    args = parser.parse_args()
    try:
        records = inventory(args.repository)
    except InventoryError as exc:
        parser.exit(status=1, message=f"inventory: {exc}\n")
    print(json.dumps(records, ensure_ascii=True, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
