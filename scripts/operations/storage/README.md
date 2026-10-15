# Checkout storage

`worktree_location_guard.sh` checks a destination before checkout creation.
`job_checkout.sh` runs that guard, then uses a local worktree or a partial,
single-branch clone. Sparse checkout is optional; neither script selects a
replacement destination, redirects a checkout, or retries elsewhere.

For a 17,771-file checkout measured on 2026-10-15, an NTFS-formatted FUSE data
volume took 133 minutes to add and 52 minutes to remove a worktree. The host
SSD took 130 seconds to add and 33 seconds to remove it. Sparse checkout reduces
file volume but does not make an NTFS or FUSE destination acceptable.

## Start helper integration

Run this before any command that creates a checkout, directory, or branch:

```bash
worktree_location_guard.sh --dest "$W" --min-free-gb "$FLOOR" || exit $?
```

For example, a start helper can use these three lines, with both scripts on PATH:

```bash
W="$CHECKOUT_ROOT/$CHECKOUT_NAME"
worktree_location_guard.sh --dest "$W" --min-free-gb "$FLOOR" || exit $?
job_checkout.sh --repo "$REPO" --branch "$BRANCH" --base "$BASE" --dest "$W" --min-free-gb "$FLOOR"
```

Integration with individual start helpers is separate work. The guard creates
nothing, including on refusal. Its arguments are:

```text
worktree_location_guard.sh --dest <dir> [--min-free-gb <n>]
```

The floor defaults to `JOB_CHECKOUT_MIN_FREE_GB` when set, otherwise 50.
An explicit option overrides the environment. Nonnegative decimal floors are
accepted. Space is read using `df -Pk`; GB means 1,048,576 KiB here (GiB).
Comparison uses the unrounded space value; output shows one decimal place.

| Exit | Meaning |
| --- | --- |
| 0 | Safe location with enough space; prints `worktree_location=ok fs=<type> free_gb=<n> dest=<dest>`. |
| 2 | Missing or invalid arguments, branch, base, or sparse profile. |
| 3 | NTFS/FUSE type, unreadable filesystem type, or inaccessible ancestor. |
| 4 | Space below the floor, or unreadable free-space information. |

The guard finds the nearest existing ancestor, resolves its symlinks, and probes
it with `stat -f -c %T -- <ancestor>`. If that probe fails or returns an unknown
type, it tries `findmnt -n -o FSTYPE --target <ancestor>`. Failure of both probes
refuses the start. The single `SLOW_TYPES` list refuses `fuseblk`, `fuse`,
`fuse.*`, `ntfs`, `ntfs3`, and `ntfs-3g`. Other types pass the location check,
including `ext2/ext3`, `xfs`, `btrfs`, `tmpfs`, and `overlayfs`.
Passing identifies a filesystem type and space at the instant of the check;
it does not prove SSD hardware or reserve space against concurrent use.

## Checkout helper

```text
job_checkout.sh --repo <canonical-checkout-or-URL> --branch <new-branch> --base <ref> --dest <dir> [--profile <name>] [--min-free-gb <n>] [--dry-run]
```

The guard runs in both modes before any Git operation. A refusal propagates its
exit code and creates no checkout, branch, worktree registration, or clone.
`--dry-run` prints `location=ok` and a plan after the real probes; it does not
validate remote availability or reserve the branch or destination.

A local repository uses `git worktree add --no-checkout`. Other sources use
`git clone --filter=blob:none --single-branch --no-checkout`, followed by branch
creation without materializing files. Remote bases must name a branch;
`main`, `origin/main`, and `refs/heads/main` select the same remote branch.
Local bases may be any existing commit reference. Servers must support blob
filtering to obtain the history-size saving; local-path clones are worktrees,
while a `file://` URL explicitly selects the clone path.

With `--profile code` and a repository basename of `digitalmodel` (optionally
ending in `.git`), the helper reads
`config/storage/sparse-profiles/digitalmodel-code.txt` and runs cone-mode sparse
checkout before the final checkout. Root files are included by cone mode.
Without a profile it explicitly selects a full checkout, even when the source
uses sparse checkout. No profile is enabled by default.

`GIT_LFS_SKIP_SMUDGE=1` is exported for all child commands, and the destination
has `core.untrackedCache=true` and `lfs.fetchexclude=*`. No LFS command is run.
For linked worktrees, these settings are worktree-specific. On first use, the
helper enables Git's shared `extensions.worktreeConfig` extension and migrates
existing `core.bare` and `core.worktree` values into the primary worktree's
configuration, as required by Git. This changes source repository metadata;
local worktree mode therefore requires write access to that metadata. It does
not change tracked source files. Use a URL clone when the source is read-only.
Sparse settings and LFS exclusions are not applied to the primary checkout.

A successful checkout prints:

```text
checkout_kb=<n> mode=<worktree|partial-clone> profile=<name|none> location=ok
```

`checkout_kb` comes from `du -sk` and includes the clone's local Git metadata
when using a clone. An error after Git starts is returned without cleanup or
retry; partially created outputs remain for inspection. Git errors retain
Git's exit code rather than the guard's 2/3/4 classification.

A measured code-profile worktree occupied 485,948 KiB (474.6 MiB), including
340,636 KiB in `tests/`. This exceeded the anticipated roughly 200 MB;
the prescribed profile retains that directory. The measurement used a temporary
shared bare source borrowing the canonical repository's objects, so the
canonical checkout remained read-only. Sparse checkout is a content selection,
not a size guarantee.

If a later operation needs another base, fetch it explicitly:

```bash
git fetch --filter=blob:none origin <base>
```

## Local tests

The tests use disposable repositories and stub only filesystem probes in the
fixtures. No NTFS/FUSE volume is needed. Run from the repository root, directing
pytest temporary files outside the checkout as appropriate:

```bash
uv run --no-project --with pytest python -m pytest tests/operations/storage -q -rA -p no:cacheprovider
bash -n scripts/operations/storage/worktree_location_guard.sh scripts/operations/storage/job_checkout.sh
shellcheck scripts/operations/storage/worktree_location_guard.sh scripts/operations/storage/job_checkout.sh
```
