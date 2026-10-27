# Repository origin status example

This standalone Python example reports an explicit list of repositories,
including the hub. It reads local Git state and cached upstream references;
it does not contact remotes. Skill wiring and automatic synchronization
integration are deferred.

Save the Python fence verbatim as `repository_origin_status.py` outside the
repositories being inspected. With the hub as the current directory, pass `.`
explicitly so that the hub appears alongside the other repositories:

```sh
python3 ../repository_origin_status.py . ../library
```

Each argument identifies a repository; there is no submodule discovery or
implicit hub omission. Paths containing spaces must be quoted by the caller.
The `Repo` column uses each resolved directory's basename, in argument order.
Basenames should be distinct and contain no pipe or newline characters.

```python
import os
import subprocess
import sys
from pathlib import Path


def git(repo, *arguments):
    # Discard inherited repository, index and configuration overrides.
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    # git(1), GIT_OPTIONAL_LOCKS: disable optional index refresh writes.
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )


def require_success(result, repo):
    if result.returncode:
        raise SystemExit(f"Cannot read {repo.name}; Git query failed.")
    return result.stdout


def row(path):
    repo = Path(path).resolve()
    status = require_success(
        git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all"), repo
    )
    # git-status(1), Porcelain Format Version 1: XY is two bytes; -z uses
    # NUL-delimited records, with an extra source-path record for renames/copies.
    # Counts start at the empty set and add one per enumerated change record.
    uncommitted = untracked = 0
    records = iter(status.split(b"\0"))
    for record in records:
        if not record:
            continue
        xy = record[:2]
        if xy == b"??":
            untracked += 1
        elif xy != b"!!":
            uncommitted += 1
            if b"R" in xy or b"C" in xy:
                next(records)

    branch_result = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    # git-symbolic-ref(1), Exit status: one means HEAD is not symbolic.
    if branch_result.returncode == 1:
        branch = "(detached)"
    else:
        branch = require_success(branch_result, repo).decode().strip()

    upstream = git(repo, "rev-parse", "--verify", "--quiet", "@{upstream}")
    if upstream.returncode:
        ahead = behind = "?"
        label = "unknown upstream"
    else:
        # git-rev-list(1), --left-right --count: local-only then upstream-only.
        counts = require_success(
            git(repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}"),
            repo,
        )
        ahead, behind = map(int, counts.split())
        if ahead and behind:
            label = "diverged"
        elif ahead:
            label = "ahead"
        elif behind:
            label = "behind"
        else:
            label = "clean"

    if uncommitted or untracked:
        label = "dirty (unknown upstream)" if upstream.returncode else "dirty"
    return repo.name, branch, ahead, behind, uncommitted, untracked, label


if __name__ == "__main__":
    if not sys.argv[1:]:
        raise SystemExit("usage: repository_origin_status.py REPOSITORY [REPOSITORY ...]")
    rows = [row(path) for path in sys.argv[1:]]
    print("Repo | Branch | Ahead | Behind | Uncommitted | Untracked | Status")
    for values in rows:
        print(" | ".join(map(str, values)))
```

`Uncommitted` counts tracked change entries, including staged, unstaged,
deleted, conflicted and renamed paths. A path changed in both the index and
the working tree counts once; a rename or copy counts once. `Untracked` counts
individual untracked files, including files inside untracked directories.
Ignored files are excluded. NUL records preserve spaces and newlines in
changed filenames.

`Ahead` and `Behind` count commits reachable only from `HEAD` and only from its
configured upstream, respectively. That upstream is often an origin tracking
branch, but may use another remote or a local branch. No assumption about the
remote name or branch name is made. These counts reflect the last locally
available upstream state and may be stale. An unresolved upstream, including
an absent tracking reference or an unborn branch, produces `?` in both columns,
never fabricated zero counts. Detached HEAD is shown as `(detached)`.

Status precedence is explicit: any tracked or untracked change produces
`dirty`, even when the branch is ahead, behind or diverged. Counts remain
visible. Dirty repositories with an unresolved upstream show
`dirty (unknown upstream)`. Otherwise an unresolved upstream shows
`unknown upstream`; known upstreams show `diverged` before `ahead` or `behind`,
then `clean` when neither side has unique commits. Other status, branch or
revision-count query failures terminate with a nonzero exit instead of
reporting a clean row. Queries are sequential observations, not an atomic
snapshot of repositories being changed concurrently.

The following independent hand calculations define the core fixtures in
[the executable tests](../../tests/docs/test_repository_origin_status_example.py).
Empty commit sets have cardinality zero. The ahead fixture has local-only
commits `{a, b, c}`; behind has upstream-only commits `{d, e}`; diverged has
local-only `{a, b}` and upstream-only `{c, d, e}`. The tracked fixture enumerates
staged, unstaged, doubly modified and deleted paths; the untracked fixture
enumerates two files. The hub fixture has empty sets and no changes.

| Repo | Branch | Ahead | Behind | Uncommitted | Untracked | Status |
| --- | --- | --- | --- | --- | --- | --- |
| workspace-hub | topic/example | 0 | 0 | 0 | 0 | clean |
| ahead | topic/example | 3 | 0 | 0 | 0 | ahead |
| behind | topic/example | 0 | 2 | 0 | 0 | behind |
| diverged | topic/example | 2 | 3 | 0 | 0 | diverged |
| tracked-changes | topic/example | 0 | 0 | 4 | 0 | dirty |
| untracked | topic/example | 0 | 0 | 0 | 2 | dirty |
| no-upstream | topic/example | ? | ? | 0 | 0 | unknown upstream |

Table: Expected rows derived from the enumerated fixture sets and paths.

The format constants and query semantics are specified by the installed Git
manuals: `git-status(1)` sections *Porcelain Format Version 1* and
*Submodules*; `git-rev-list(1)` options `--left-right` and `--count`;
`git-symbolic-ref(1)` section *Exit status*; `git-rev-parse(1)` options
`--verify`, `--quiet` and upstream revision syntax; and `git(1)` environment
variable `GIT_OPTIONAL_LOCKS`. Submodule changes are tracked entries in the
containing repository; list a submodule explicitly to inspect its own commits
and untracked files. The tests also enumerate dirty precedence combinations,
rename source records, detached and unborn branches, read failures, inherited
Git bindings and rejection of write commands. They execute the exact fence in
a temporary directory without invoking real Git or changing source fixtures.
