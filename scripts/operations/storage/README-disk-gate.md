This is the disk gate section to be combined into `README.md`.

# Storage operations

The disk gate checks disk floors and reports storage consumers.
The worktree location guard and checkout helper check checkout destinations.

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
reviewing the report. Remote archives use `HOST:DIR`; transfers use `rsync -a`
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
