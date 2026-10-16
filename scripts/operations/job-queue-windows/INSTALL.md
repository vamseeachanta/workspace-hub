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
   The example `start` command only creates a worktree; it does not execute jobs
   or call cleanup. Its command dispatch must not replace the live dispatch.
7. Against a disposable queue, run `pump.ps1 -ConfigPath <config> -DryRun` and
   `bash run-job.sh cleanup <id> none <config> --dry-run`. Confirm gate logs,
   the selected job, keep reasons, and that nothing launches or is removed.
8. Test the merged live scripts with disposable jobs: occupied slots, total and
   per-repository limits, repeated passes, execution, publication, and cleanup.
   Do not resume the live queue until these integration checks pass.
9. Remove the pause file and watch the first gate, launch and cleanup logs.
10. Roll back by pausing, restoring the backup, checking digests, then resuming.

No installation or live-script execution is performed by this repository change.
Existing worktrees under the old root require a separate reviewed cleanup.
