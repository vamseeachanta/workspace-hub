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
literal `all` selects the retry batch; it is not a job to start. At most 32 due
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
size-probe failures are recorded as `unknown`.
`run-job.sh cleanup-recent all none <config> --dry-run` also preserves retry
markers. Run under Git Bash with `/usr/bin` first on `PATH` so `find` is GNU find.

`-FreeSpaceProbe` and `-Launcher` are explicit PowerShell test parameters; ambient
environment variables cannot replace the disk measurement or launcher.
The pump performs one pass and starts at most one job. The live pump must retain
atomic slot acquisition and enforce its configured start and concurrency limits.
