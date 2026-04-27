# Execute Now — ace-linux-2 Overflow Worker

You are a real Claude Code worker running on ace-linux-2. Execute useful overflow work now; do not merely plan.

Read and follow the full machine-role instructions from `/tmp/ace-linux-2-continuous-parallel-work-prompt.md`, with these explicit overrides for this run:

1. Treat ace-linux-2 as a worker only. `gh auth` is known invalid unless your fresh check proves otherwise; do not post labels/comments/closures. Instead write local report files for ace-linux-1 to post later.
2. Do not touch #2518 or `/mnt/local-analysis/reconcile-main-20260427`.
3. Do not duplicate active ace-linux-1 Codex lanes for #2462 or #2458. Also inspect #2227/#2464 before starting anything; skip if active/dirty.
4. Priority execution lane: if safe and plan-approved, work on #2464 in an isolated local worktree or clone under `/mnt/local-analysis/ace2-codex-work/issue-2464`.
5. If #2464 is unavailable or not plan-approved, choose one safe `agent:codex,status:plan-approved` overflow candidate from the prompt (#2124, #2125, #2126, #1962) and execute bounded work in an isolated worktree.
6. Use real CLI execution. Prefer Codex for implementation work. If launching Codex and it hangs waiting for stdin, adapt by using the local process/shell pattern available on ace-linux-2; do not leave zombie processes.
7. Follow TDD/validation. Commit only issue-scoped changes locally and push a branch only if `git`/remote auth allows normal non-force push. If push/auth fails, leave the local commit and write exact recovery instructions.
8. Always write an ace-linux-1 handoff report under `/mnt/local-analysis/ace2-worker-reports/` containing: issue number, worktree path, branch, commit SHA if any, validation commands/results, changed files, push status, GitHub comment body ace-linux-1 should post, blockers.

Final output should point to the report file(s).
