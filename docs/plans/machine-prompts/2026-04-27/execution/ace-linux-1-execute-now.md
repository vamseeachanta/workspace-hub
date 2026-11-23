# Execute Now — ace-linux-1 Control Plane

You are a real Claude Code control-plane worker running on ace-linux-1. Execute the continuous work mission now; do not merely plan.

Read and follow `/mnt/local-analysis/workspace-hub/docs/plans/machine-prompts/2026-04-27/ace-linux-1-continuous-parallel-work-prompt.md`, with these explicit overrides for this run:

1. Do not touch `/mnt/local-analysis/reconcile-main-20260427` while the #2518 finalizer process is active. You may only observe #2518 via `gh issue view`, `git ls-remote`, and process checks. If the finalizer finishes, verify and post/close only if still needed.
2. Do not duplicate active Codex lanes. Active/known lanes include #2462 and #2458; #2227 and #2464 must be rechecked before relaunch.
3. Treat ace-linux-2 worker as potentially started in tmux session `ace2-overflow-20260427`; periodically collect its report files from `/mnt/local-analysis/ace2-worker-reports/` via ssh if available, but do not block on it.
4. Use GitHub mutation authority only from ace-linux-1: labels/comments/closures must be evidence-backed.
5. Maintain 3–5 useful Codex lanes if safe; if launching new lanes, use isolated worktrees under `/mnt/local-analysis/codex-burn-20260427/`, status:plan-approved issues only, no force-push, and close stdin for Codex where necessary.
6. Write/update a dispatch ledger under `/mnt/local-analysis/codex-burn-20260427/controller-ledger-20260427.md` with active lanes, issue URLs, branches, commit/push/validation state, and next action.
7. If blocked by active git processes, do not kill unrelated work unless it is clearly stale and exact PID/PGID is known. Prefer observation and ledger updates.

Final output/log should summarize actions taken, process/session IDs launched, GitHub mutations made, and blockers.
