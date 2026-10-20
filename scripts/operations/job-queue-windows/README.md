# Windows Job Queue Scripts

This folder contains the versioned integration examples of the Windows job queue pump, runner, and launchers. The live queue is not installed from this checkout automatically; installation is a separate reviewed operation.

The scripts read their local values from `job-queue.local.conf`, which is intentionally not committed. Use `job-queue.local.example.conf` as the template. The configuration supplies:

- `QUEUE_ROOT`: local queue folder.
- `CLONE_ROOT`: folder containing the shared repository clones.
- `WORKTREE_ROOT`: short folder where new job worktrees are created.
- `JOB_BRANCH_PREFIX`: branch prefix used to identify each job's own branch.
- `DEFAULT_REPOSITORY`: repository used when a job spec omits `REPO`.
- `REPOSITORY_ALLOW_LIST`: comma-separated local repository allow-list.
- `MIN_DISK_FREE_GB`: disk floor; values below 50 are raised to 50.
- `BASH_EXECUTABLE`: optional Bash executable; defaults to `bash`.

The committed scripts are neutralized for a public repository. They contain no live queue path, repository namespace, default repository name, or private allow-list.

The pump and runner are partial examples. Merge their new functions into the live
scripts as described in `INSTALL.md`; preserve execution and concurrency controls.
The live runner calls cleanup after publication, result writing and slot release.
The example `start` command only creates a worktree. Existing branches require a
matching `JOB_BRANCH_PREFIX` before cleanup can consider them.

Lock a job worktree (`git worktree lock`) before working in it by hand.
Cleanup keeps Git-locked worktrees and worktrees with files or administrative
entries touched in the last 60 minutes. Set the environment variable
`WORKTREE_KEEP_MINUTES` to a positive integer to override that interval.
Failed lock or activity probes keep the worktree and record the reason.

The review's later-pass option retains that activity window. A keep caused only
by recent activity creates `logs/recent-cleanup/<id>`. Each unpaused pump pass
calls `run-job.sh cleanup-recent all none <config>` before disk admission and
queue selection, including when the queue is empty or disk space is low. The
literal `all` selects the retry batch; it is not a job to start. At most six due
markers are retried per invocation, after a full retention interval since the
last keep or failed attempt. Each retry calls the existing `cleanup <id>` path
and rechecks every guard. New activity postpones another attempt; another keep
reason removes the marker and leaves the worktree for manual disposition.
Successful removal clears the marker. Identical keep-log records are not appended
again. This requires later invocations of the integrated pump; no scheduler is
installed and a stopped or paused pump cannot reclaim worktrees.

`pump.ps1 -DryRun` probes both disks and applies queue gates without launching.
`run-job.sh cleanup <id> none <config> --dry-run` prints the keep reason or
"would remove" without changing worktrees or the keep log. Keep-log sizes use KiB;
size-probe failures, empty output and timeouts are recorded as `unknown`. Size
collection has a two-second limit and one-second forced-kill grace period. A
non-recent retry marker is removed only after its keep record is written.
`run-job.sh cleanup-recent all none <config> --dry-run` also preserves retry
markers. Run under Git Bash with `/usr/bin` first on `PATH` so `find` is GNU find.

Each due marker is refreshed before the child starts, so interruption also backs
off that entry for a full retention interval. GNU coreutils `timeout` bounds the
remote probe to 15 seconds and each whole attempt to 90 seconds, each followed by
a two-second forced-kill grace period. A remote timeout keeps the tree as not
pushed. An entry timeout writes `cleanup attempt timed out` to the keep log and
ends automatic retries for that tree. Inspect it because interrupted removal may
be partial. Six bounded entries, including fallback size probes, fit below the
ten-minute outer wait apart from scheduling and record-writing overhead. Later
entries can still run. These bounds are limits, not full-size timing measurements.
Dry-run leaves marker times unchanged, including when a probe times out.

The pump starts cleanup in a login shell (`-lc`) with absolute runner and
configuration paths. It sets `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=never`.
The whole pass has a ten-minute outer bound; on expiry, `taskkill /T /F` terminates
the child tree. Output goes to `logs/recent-cleanup.out`, allowing the pump to
report partial progress without waiting on inherited pipes. A timeout does not
establish whether earlier entries were removed; inspect that output and the keep
log. Preserve these controls when integrating functions into live scripts.

The pump uses the largest disk floor from configuration, `min_disk_free_gb` in
the limits file, and 50 GB. Invalid floor values hold cleanup and admission with
a log reason.
The runner independently enforces the configuration floor before creating a tree;
set it at least as high as the limits-file floor for direct launcher use.

`-FreeSpaceProbe` and `-Launcher` are explicit PowerShell test parameters; ambient
environment variables cannot replace the disk measurement or launcher.
The pump performs one pass and starts at most one job. The live pump must retain
atomic slot acquisition and enforce its configured start and concurrency limits.

Cleanup requires the result record to begin with `OK`. Failed and empty results
are retained. Every cleanup attempt probes the remote job branch with interactive
authentication disabled and the existing bounded timeout. Cached tracking refs
do not establish publication: a deleted or unreachable remote branch keeps the
worktree. A remote descendant is accepted only when local objects establish
ancestry; unknown remote objects keep the worktree.

Disk admission compares unrounded availability. The legacy `GB` configuration
keys use binary GiB in both scripts, retaining the existing more restrictive
interpretation of the issue's 50 GB minimum. For example, 49.96 GiB remains below
the 50 GiB floor even though display rounding would give 50.0 GiB. These input
values illustrate the boundary; they are not measured disk availability.

The reproducible storage comparison is documented in
`docs/operations/job-queue-worktree-footprint.md`. No live queue installation or
job execution is established by the stand-in tests or storage measurements.
