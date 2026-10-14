# Install Procedure

This procedure is performed only after an independent review accepts the change.

1. Place the documented pause file in the local queue folder and confirm the pump records a hold line.
2. Record SHA-256 digests of the live pump, runner, launchers, and limits file.
3. Copy the live files to a dated backup folder outside the repository.
4. Create the local `job-queue.local.conf` from `job-queue.local.example.conf`.
5. Create the configured short worktree root if it does not already exist.
6. Copy `pump.ps1`, `run-job.sh`, `launch.ps1`, `launch.sh`, and `limits.txt` from this folder into the queue script location.
7. Run a dry-run pump pass against a stand-in queue folder and confirm no live job starts.
8. Remove the pause file.
9. Watch the first pump log lines for the disk-floor fields, selected job, launcher result, and any kept-worktree entries.
10. Roll back by pausing the pump, restoring the backed-up files, confirming the backup digests, and lifting the pause.

Existing worktrees under the old worktree root are intentionally left in place. Their removal is a separate reviewed cleanup.
