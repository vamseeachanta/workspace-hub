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

Lock a job worktree (`git worktree lock`) before working in it by hand.
Cleanup also keeps worktrees whose files or administrative entries were touched
in the last 60 minutes. The environment variable `WORKTREE_KEEP_MINUTES` overrides
that interval with a positive integer. Confirm locked and recently touched trees
report a keep reason in both dry-run and normal cleanup before resuming work.

Use Git Bash with `/usr/bin` first on `PATH`; the activity and retry probes require
GNU find, not the Windows text-search command. Use the same environment, retention
override and configuration for immediate cleanup and later pump invocations.
`min_disk_free_gb=50` is the sole disk-floor key in the example limits file;
`min_free_gb` is obsolete and is not read.

Recent-only keeps create retry markers in `logs/recent-cleanup/`. The existing
pump invocation cadence supplies the later pass; this change installs no timer
or persistent scheduler. After the configured interval, at most 32 due markers
are retried, with all cleanup guards reevaluated. New activity refreshes the retry
interval. Another guard failure stops automatic retries for that tree and leaves
its reason in the keep log. Resolve that condition before a manual cleanup call.
Repeated identical keep records are suppressed. Existing keep-log rows from an
older integration have no retry marker: re-enroll them only through a reviewed
`cleanup <id>` call, which rechecks all guards. No historical row authorizes removal.
