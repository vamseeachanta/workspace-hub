# Storage operations

The disk gate checks disk floors and reports storage consumers.
The worktree location guard and checkout helper check checkout destinations.

## Worktree location guard

`worktree_location_guard.sh` checks a destination before checkout creation.
`job_checkout.sh` runs that guard, then uses a local worktree or a partial,
single-branch clone. Sparse checkout is optional; neither script selects a
replacement destination, redirects a checkout, or retries elsewhere.

For a 17,771-file checkout measured on Linux on 2026-10-15, an NTFS-formatted
FUSE data volume took 133 minutes to add and 52 minutes to remove a worktree. The host
SSD took 130 seconds to add and 33 seconds to remove it. Sparse checkout reduces
file volume but does not make an NTFS or FUSE destination acceptable on Linux.

### Worktree location guard: Start helper integration

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
accepted. On Linux, space is read using `stat -f -c '%a %S'` (available blocks
times bytes per block). If unavailable or invalid, `df -Pk` is parsed using its
capacity field and the three preceding numeric fields; source or mount names
containing spaces do not shift Available. Windows uses that same `df` parsing.
GB means 1,048,576 KiB here (GiB).
Comparison uses the unrounded space value; output shows one decimal place.

| Exit | Meaning |
| --- | --- |
| 0 | Safe location with enough space; prints `worktree_location=ok fs=<type> free_gb=<n> dest=<dest>`. |
| 2 | Missing or invalid arguments, branch, base, or sparse profile. |
| 3 | Refused Linux filesystem type, unreadable type, inaccessible ancestor, or network/unclassified Windows destination. |
| 4 | Space below the floor, or unreadable free-space information. |

The guard finds the nearest existing ancestor and resolves its symlinks. On Linux,
it probes that ancestor with `stat -f -c %T -- <ancestor>`. If that probe fails
or returns an unknown type, it tries `findmnt -n -o FSTYPE --target <ancestor>`. Failure of both probes
refuses the start. The single `SLOW_TYPES` list refuses `fuseblk`, `fuse`,
`fuse.*`, `ntfs`, `ntfs3`, `ntfs-3g`, `9p`, `v9fs`, `drvfs`, `cifs`,
`smb`, `smb2`, `smb3`, `nfs`, `nfs3`, and `nfs4`. Other Linux types pass
the location check, including `ext2/ext3`, `xfs`, `btrfs`, `tmpfs`, and `overlayfs`.
Passing identifies a filesystem type and space at the instant of the check;
it does not prove SSD hardware or reserve space against concurrent use.

On Windows, `uname -s` beginning with `MINGW`, `MSYS` or `CYGWIN` selects a
separate branch; Linux type probes are not used. Git for Windows supplies
`cygpath -m` to convert the resolved ancestor. A PowerShell executable on PATH
queries `Win32_LogicalDisk.DriveType`; only a local fixed drive (type 3) passes.
Native NTFS on a local Windows drive is accepted. UNC paths, mapped network
drives, and destinations that cannot be classified are refused with exit 3 and
"network or non-local path". Missing conversion or classification tools also
refuse. The free-space floor still applies with exit 4. Linux is the measured
platform; Windows behavior is covered by stubs, without a native Windows run.
macOS is not supported.

### Worktree location guard: Checkout helper

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

### Worktree location guard: Relation to the disk gate and to the lean clone profile

The guard's floor is the lowest free space a job checkout needs. A start helper
passes its value from the disk gate's per-filesystem settings using
`--min-free-gb`. Exit 4 here means the checkout floor was not met or could not be
read. Exit 4 also means low free space in the disk gate, which additionally
blocks on capacity and inode thresholds or unreadable measurements. Both refuse
the start. The worktree guard's exit 3 refuses slow or unclassified destinations;
the disk gate's exit 10 warns and exit 2 signals settings or argument errors.
The guard does not read the disk gate settings itself.

`scripts/workstations/clone_profile.py` is the other lean-clone facility: use it
for an explicit shallow, blob-filtered workstation clone with selected sparse
directories. It has no location guard. Use `job_checkout.sh` for a guarded job
checkout that prefers a linked worktree and otherwise uses a single-branch
partial clone, with an optional repository profile. Call the location guard
separately before creating a checkout with the clone-profile facility.

The disk gate is documented under `## Disk gate`, including
`### Consumer inspection` and `### Temporary-folder sweep`.
Distinct section headings allow both sets of instructions to coexist.

### Worktree location guard: Local tests

The tests use disposable repositories and stub platform and filesystem probes
in the fixtures. No NTFS/FUSE volume is needed. Run from the repository root, directing
pytest temporary files outside the checkout as appropriate:

```bash
uv run --no-project --with pytest python -m pytest tests/operations/storage -q -rA -p no:cacheprovider
bash -n scripts/operations/storage/worktree_location_guard.sh scripts/operations/storage/job_checkout.sh
shellcheck scripts/operations/storage/worktree_location_guard.sh scripts/operations/storage/job_checkout.sh
```

## Disk gate

The gate checks every configured filesystem before a job starts. It never stops
running work and never prunes a cache. Bash uses `df -Pk` for capacity and `df -Pi`
for inode use; the PowerShell version reads filesystem drives with `Get-PSDrive`.
Use `bash disk_gate.sh` under Linux or Git Bash; use `disk_gate.ps1` on Windows.

Settings are whitespace-delimited data, with one host's filesystems per file.
Paths containing whitespace, tabs or newlines are unsupported. Settings are never
sourced as shell code. Blank lines and whole-line comments are accepted.

```text
/ warn_pct=85 block_pct=90 floor_gb=50
/data warn_pct=85 block_pct=90 floor_gb=300
cache uv /cache/uv cap_gb=20
cache npm /cache/npm cap_gb=5
cache pip /cache/pip cap_gb=3
cache pre-commit /cache/pre-commit cap_gb=3
cache work-cache /cache/work cap_gb=10
cache work-temp /cache/temp cap_gb=10
tmp /tmp old_days=3 cap_gb=5
```

The example is a format illustration, not installed configuration. Use drive
names such as `C:` in the Windows file. `--mount PATH` may repeat to select a
configured subset; PowerShell accepts `-Mount` as an array. Unknown selections or
invalid/unreadable settings return 2. Defaults are 85% warning, 90% blocking,
zero free-space floor, and the cache caps shown above. Sizes use binary GiB
(1,073,741,824 bytes) although the setting key is `floor_gb` or `cap_gb`.

| Exit | Meaning |
| --- | --- |
| 0 | All selected disks are below their warning threshold |
| 10 | A disk warns, or explicit consumer inspection reports a cap or unknown measurement |
| 4 | A disk reaches its block percentage, falls below its free floor, reaches 95% inode use, or cannot be read |
| 2 | Settings are unreadable or invalid; do not start |
| Other than 0 or 10 | Do not start, including 1, 4, 124, 126, 127, 130, 137 and 143 |

Exit 4 also represents low space in the worktree location guard of #4083.
The highest severity across selected disks wins, independently of numeric codes.
Equality warns at 85% and blocks at 90%; free space equal to its floor is permitted. Windows exposes no inode
accounting through `Get-PSDrive`, so `inode_pct` is null there. `--json` (Windows:
`-Json`) writes newline-delimited JSON objects, one per disk, with `mount`,
`size_kb`, `used_kb`, `free_kb`, `used_pct`, `inode_pct`, and `state`. Unreadable
values are null. Parsing failures never become healthy readings.

A start helper can capture the result without losing nonzero status:

```bash
rc=0
bash scripts/operations/storage/disk_gate.sh --conf "$CONF" || rc=$?
# During the first 24 hours, log all outcomes and continue starting work.
# After that observation period, enable this refusal branch:
case $rc in
  0|10) ;;
  *)
    printf '=== %s NOT-LAUNCHED disk gate: %s %s %s\n' \
        "$job" "$mount" "$used_pct" "$free_gb"
    exit "$rc" ;;
esac
```

The helper must obtain `mount`, `used_pct`, and `free_gb` from the gate report for
each blocked disk; they are illustrative variables above. Log warnings and permit
the start on 10. Activate refusal only after a 24-hour warn-only observation
period. Installing settings and changing start helpers are separate work.

### Consumer inspection

`bash disk_gate.sh --conf "$CONF" --consumers [--json]` explicitly refreshes
measurements older than six hours. Each `du -sk` has a 15-second timeout and idle
I/O priority through `ionice -c 3`; missing tools, inaccessible paths and timeouts
produce UNKNOWN. Fresh cached cap excesses also warn during normal starts. The normal start path
never invokes `du`. It reads only a fresh
snapshot and lists configured consumers, largest first, whenever a disk blocks.
Without a fresh snapshot it lists unknown values. A writable settings directory
allows a private `.consumers.tsv` snapshot beside the settings; a read-only
settings directory still permits inspection but cannot retain the snapshot.

The snapshot is bound to the settings checksum and measurement time. A consumer
record has `path`, `bytes`, `cap_bytes`, and `state`. A cap exceeded alone warns
with exit 10 and cannot produce 4. Inspection lists configured paths across the
host; consumers must be configured on the appropriate filesystem by the settings
author. The gate cannot attribute shared or nested mounts from path names alone.

A `tmp` line adds the whole tree with a 15 GiB cap, an old top-level directory
total/count with a 5 GiB default cap, and the five largest old directories. The
`cap_gb` on that line overrides the old-directory cap. The old-directory report
uses directory modification times, not sweep eligibility. Inspect it separately
from the sweep's stricter newest-entry and process checks. Large old-directory
sets can require multiple bounded reads; schedule refreshes outside job starts.

Pruning belongs to each tool's own command (`uv cache prune`, `npm cache verify`,
`pre-commit gc`) in a scheduled maintenance window, or when a cache exceeds its
cap and no job is running. These scripts never invoke those commands.

### Temporary-folder sweep

`bash tmp_sweep.sh` reports candidate folders beneath `/tmp` without modifying
them. Use `--root DIR` for another temporary tree and `--move ARCHIVE` only after
reviewing the report. A root that resolves to the filesystem root is refused
with exit 2 before any scan or archive action; empty or whitespace-only roots
are also refused. Remote archives use `HOST:DIR`; transfers use `rsync -a`
with one filesystem per transfer. The rsync SSH transport keeps its standard
input; standalone SSH commands use `-n`. No running process is stopped.

The sweep keeps hidden folders, symlinks, recently modified trees, trees owned by
another user, sockets, read-only entries, process-referenced trees, and Git work
with dirty state or commits absent from remotes. Bare repositories are retained. Missing inspection capabilities
or unreadable Git state prevent a move. Process inspection uses `/proc` by default;
`TMP_SWEEP_PROC_ROOT` selects an alternative process tree for isolated tests.
An unreadable process view keeps the folder unless that process has a different
owner and the folder and every entry deny all group and other access. The report
counts distinct foreign processes skipped during the scan. Root-owned processes
can still access private trees and are unchecked when skipped. Root with explicit
`--uid UID` inspects folders owned by that UID; root or `CAP_SYS_PTRACE` can remove
the process-view restriction where process access policy permits. An unreadable
same-owner view always keeps the folder.

Device changes and mount-table entries at or below a candidate keep it with
`mount-point`, including bind mounts on the same device. All tree traversal,
copying and removal stay on one filesystem. Missing mount information keeps the
folder. Copies are compared by file count, byte total and entry count before
guarded source removal; unsuccessful verification leaves the source in place. Remote attempts use unique staging directories; partial copies
are retained for inspection and do not occupy the final archive name or prevent
a retry. The final name is assigned only after verification. A `MANIFEST.tsv`
records archival outcomes. Source removal can still fail, in which case both copies remain and the outcome is reported.

Archival requires a quiescent tree: checks immediately before removal reduce but
cannot eliminate races with a process that starts or writes after inspection.
Use report mode while jobs run. Automated destructive cleanup is outside the
gate's role. Remote archival requires compatible tools at the destination and
is exercised offline with rsync and an SSH command fixture; no network transfer
is established by those tests.
