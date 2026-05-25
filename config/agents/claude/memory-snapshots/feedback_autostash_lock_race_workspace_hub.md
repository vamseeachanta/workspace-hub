---
name: autostash-lock-race-workspace-hub
description: "git rebase --autostash fails (\"Cannot autostash\") when statusline-command.sh git status loops race with stash creation on workspace-hub"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 000d04a3-532a-4959-becb-59b1f1349fb3
---

`git pull --rebase --autostash` repeatedly fails with `fatal: Cannot autostash` in `workspace-hub` long-running sessions, even after killing zombie git processes. Root cause: Claude Code's `statusline-command.sh` runs `git status` every few seconds (which transiently acquires `.git/index.lock`), and that lock-acquisition window races with the autostash's own lock acquisition — too tight to survive on this repo.

**Why:** Discovered 2026-05-22 during a kanban push attempt. Sequence: `git pull --rebase --autostash` → fatal: Cannot autostash → no progress. Killing zombies and clearing stale `.git/index.lock` only delayed the next race by seconds. Direct `git stash push -u -m "label"` also failed silently (stash list showed no new entry with my label). The lock-storm window from statusline's tight loop is faster than autostash's lock-grab attempt.

**How to apply:**
- Don't use `--autostash` on workspace-hub under load. Either (a) commit dirty files explicitly via `git add -u && git commit` (tight sequence retry-loop blocked by [[feedback_retry_loop_sweep_contamination]] guardrails), or (b) push from an isolated worktree where the main `.git/index.lock` doesn't matter.
- The cleanest path for "push my one commit": push to a feature branch with `git push origin <sha>:refs/heads/<branch>` — doesn't require clean WT, doesn't rebase, doesn't conflict with concurrent sessions. Then PR + merge via GitHub UI.
- Worktree-isolated rebase ALSO has issues: workspace-hub's 19455-file materialization is indeterminate under parallel-agent I/O load. See [[worktree-materialization-variance-workspace-hub]].
