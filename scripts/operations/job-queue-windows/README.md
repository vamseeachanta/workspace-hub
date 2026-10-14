# Windows Job Queue Scripts

This folder contains the versioned copy of the Windows job queue pump, runner, and launchers. The live queue is not installed from this checkout automatically; installation is a separate reviewed operation.

The scripts read their local values from `job-queue.local.conf`, which is intentionally not committed. Use `job-queue.local.example.conf` as the template. The configuration supplies:

- `QUEUE_ROOT`: local queue folder.
- `CLONE_ROOT`: folder containing the shared repository clones.
- `WORKTREE_ROOT`: short folder where new job worktrees are created.
- `REPOSITORY_OWNER`: repository owner used by the local runner.
- `DEFAULT_REPOSITORY`: repository used when a job spec omits `REPO`.
- `REPOSITORY_ALLOW_LIST`: comma-separated local repository allow-list.
- `MIN_DISK_FREE_GB`: disk floor; values below 50 are raised to 50.

The committed scripts are neutralized for a public repository. They contain no live queue path, account-specific owner, default repository name, or private allow-list.
