# Install Procedure

Installation is performed by the maintainers after review. The versioned pump and
runner are integration examples, not complete replacements for live scripts.

1. Place the documented pause file in the local queue folder and confirm a hold.
2. Record SHA-256 digests of the live scripts and copy them to a dated backup.
3. Create `job-queue.local.conf` from the example and create its worktree root.
4. Compare the live scripts with these examples. Preserve live slot acquisition,
   total and per-repository limits, start limits, job execution, result writing,
   publication, and release of slots. Preserve queue reselection after each start.
5. Merge the configuration, path checks, disk probe, dry-run handling and cleanup
   functions into the live scripts. Do not copy `pump.ps1` or `run-job.sh` over
   the live files. Merge launcher quoting and configuration forwarding separately;
   preserve the existing limits file and remove any obsolete duplicate disk key.
6. In the live `run-job.sh`, call `cleanup` after successful publication, result
   writing and release of the job's lock slot. Failed or unpublished jobs stay.
   Merge the `cleanup-recent` dispatch and the pump's later-pass call as well.
   On every unpaused invocation, run that pass before disk admission and queue
   selection, even when no new job can start. Preserve `CreateNoWindow` and
   captured output/exit status for the synchronous Bash child. Do not route
   cleanup through the asynchronous job launcher or acquire a job slot for it.
   Preserve the login shell (`-lc`), absolute runner/configuration paths,
   `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=never`. Preserve the ten-minute
   outer wait and `taskkill /T /F` on expiry, including partial output capture in
   `logs/recent-cleanup.out`; a timeout requires inspection of earlier progress.
   Preserve the marker refresh before each attempt and GNU coreutils `timeout`
   with a 15-second network limit, a 90-second entry limit and two-second
   forced-kill grace periods. Preserve the six-entry batch cap, bounded size
   collection with `unknown` fallback, and durable timeout keep records. These
   keep an interrupted entry from blocking every subsequent pass. Capture reads
   must share active writers and preserve the timeout action on read failure.
   The example `start` command only creates a worktree; it does not execute jobs
   or call cleanup. Its command dispatch must not replace the live dispatch.
7. Against a disposable queue, run `pump.ps1 -ConfigPath <config> -DryRun` and
   `bash run-job.sh cleanup <id> none <config> --dry-run`, then
   `bash run-job.sh cleanup-recent all none <config> --dry-run`. Confirm gate logs,
   the selected job, keep reasons, and that nothing launches or is removed.
8. Test the merged live scripts with disposable jobs: occupied slots, total and
   per-repository limits, repeated passes, execution, publication, and cleanup.
   Do not resume the live queue until these integration checks pass.
9. Remove the pause file and watch the first gate, launch and cleanup logs.
10. Roll back by pausing, restoring the backup, checking digests, then resuming.

No installation or live-script execution is performed by this repository change.
Existing worktrees under the old root require a separate reviewed cleanup.

Select a short folder on the system drive for `WORKTREE_ROOT`; retain clones in
their existing location. Confirm that the system-drive and clone-drive roots
resolve to the intended volumes before testing admission. No live root is
committed in the configuration example. Verify below-floor and exact-floor cases
on each volume using the unrounded availability; the legacy `GB` keys mean GiB.
Before installation, obtain second-provider review of the exact integrated
scripts. A repository test pass alone does not authorize installation.

Confirm failed and empty result records are kept. Disconnect the disposable
remote, then delete its job branch, testing each condition separately: both must
retain the worktree even when a local tracking ref still matches its head.
Successful cleanup must establish publication from a live remote branch probe.

Lock a job worktree (`git worktree lock`) before working in it by hand.
Cleanup also keeps worktrees whose files or administrative entries were touched
in the last 60 minutes. The environment variable `WORKTREE_KEEP_MINUTES` overrides
that interval with a positive integer. Confirm locked and recently touched trees
report a keep reason in both dry-run and normal cleanup before resuming work.

Use Git Bash with `/usr/bin` first on `PATH`; the activity and retry probes require
GNU find, not the Windows text-search command. Use the same environment, retention
override and configuration for immediate cleanup and later pump invocations.
GNU coreutils `timeout` must also be available. Configure `BASH_EXECUTABLE` if
`bash` does not resolve to the intended executable; environment overrides are
not used. The largest configured floor applies in the pump; invalid values hold
cleanup and admission. Keep `MIN_DISK_FREE_GB` at least as high as the limits-file floor so
the independent runner check protects direct launches too.
`min_disk_free_gb=50` is the sole disk-floor key in the example limits file;
`min_free_gb` is obsolete and is not read.

Recent-only keeps create retry markers in `logs/recent-cleanup/`. The existing
pump invocation cadence supplies the later pass; this change installs no timer
or persistent scheduler. After the configured interval, at most six due markers
are retried, with all cleanup guards reevaluated. New activity refreshes the retry
interval. Another guard failure stops automatic retries for that tree and leaves
its reason in the keep log. Resolve that condition before a manual cleanup call.
Repeated identical keep records are suppressed. Existing keep-log rows from an
older integration have no retry marker: re-enroll them only through a reviewed
`cleanup <id>` call, which rechecks all guards. No historical row authorizes removal.
