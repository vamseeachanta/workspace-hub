# Dirty Workspace Plan-Mode Scout Wave

Use this pattern when the user wants available Claude capacity converted into useful work, but the control repo has substantial dirty/untracked state or multiple issues already show `status:working`.

## Session Signal

A Claude-capacity wave was attempted from Telegram with ~40% Claude weekly capacity left and ~36 hours to reset. The control repo was dirty and several plan-approved issues had active `status:working` labels.

Initial attempt: create multiple isolated worktrees and prompt files. The orchestration command timed out while `git worktree add` was still running. It left directories whose `.git` files pointed to missing `.git/worktrees/*` metadata, so `git -C <worktree> status` failed with `fatal: not a git repository`.

Second attempt: launch Claude Code in plan mode using absolute prompt and output paths. First background launch used relative prompt paths and failed with `bash: <prompt>.md: No such file or directory`; relaunching with absolute paths worked.

## Safer Pattern

1. Refresh live state:
   - `git status --short`
   - `git branch --show-current`
   - `git rev-parse --short HEAD origin/main`
   - inspect live issue labels and local plan/marker presence.
2. If dirty state or worker contention exists, do **not** immediately create write-enabled implementation worktrees.
3. Write prompt files under a neutral log directory, e.g.:
   - `/mnt/local-analysis/agent-logs/<wave-id>/<lane>.md`
4. Launch read-only/plan-mode Claude lanes with absolute paths:
   ```bash
   claude -p --permission-mode plan --output-format text \
     < /mnt/local-analysis/agent-logs/<wave-id>/<lane>.md \
     > /mnt/local-analysis/agent-logs/<wave-id>/<lane>.out.md 2>&1
   ```
5. Make lanes produce durable artifacts:
   - approval-readiness report;
   - execution-readiness runbook;
   - next-safe-candidate shortlist;
   - exact future implementation prompt.
6. Add a one-shot monitor cron/job to inspect output files after a bounded interval and report back to the origin channel.

## Recovery if Worktree Creation Times Out

- Do not use the half-created directories.
- Inspect:
  ```bash
  git worktree list | grep <wave-id> || true
  find /mnt/local-analysis/worktrees/<wave-id> -maxdepth 2 -name .git -type f -print -exec head -1 {} \;
  git -C <candidate-dir> status --short
  ```
- If `.git` points to missing metadata and the worktree is not registered, treat it as broken setup state, not an implementation workspace.
- Prefer removing only the wave-specific directory after confirming it contains no real work; avoid broad cleanup in a dirty repo.

## Pitfalls

- Relative prompt paths may fail in background terminal launches even when `workdir` was intended.
- `git worktree prune` or `rm -rf` may be slow on large workspace trees; do not block the throughput wave waiting on cleanup if a read-only scout wave can proceed.
- Do not count scout lanes as implementation progress; they are queue selection, plan hardening, and safe prompt preparation.
