> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-31
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_autorun_clobbers_subagent_worktree_commits.md

---
name: feedback_autorun_clobbers_subagent_worktree_commits
description: "Autorun resets worktree branches to origin/main, clobbering un-pushed commits — push immediately"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 15eb7078-e8e9-45ff-ada1-013cdee3227d
---

2026-06-20/21 (ecosystem Pages builds): a background autorun process runs `git reset --hard origin/main` (and `git pull`/merge) on `/mnt/local-analysis/wt-*` worktrees on a cycle. It clobbered un-pushed commits TWICE: my teamresumes commit (recovered by re-committing) and a delegated subagent's assetutilities `feat/github-pages` commit (branch snapped back to an autorun merge commit, `pages.yml` left untracked on disk; the agent then stalled before pushing).

**Why:** the autorun resets the LOCAL worktree branch, but does NOT touch REMOTE branches. A pushed branch on origin is immune.

**How to apply:**
- After `git commit` in any `/mnt/local-analysis/wt-*` worktree, **push immediately** (same turn, ideally same bash command: `git add … && git commit … && git push -u origin <branch>`). The push is the protection, not the commit.
- When delegating worktree work to a subagent, the agent's report may say "done" but verify the REMOTE: `git ls-remote --heads origin <branch>` + `gh pr view`. If the local HEAD is an autorun commit and the file is untracked, the commit was clobbered — recover by re-committing the on-disk file and pushing fast.
- Files written by Write survive `reset --hard` (untracked files aren't deleted), so the content is usually still on disk to recover. `index.lock` from a live autorun `reset` (D-state PID) means a real process holds it — don't force-rm; back work out to a neutral path and retry.

See [[feedback_g1_landing_worktree_destruction_and_push_gate]], [[feedback_amend_clobbers_parallel_branch_in_shared_checkout]], [[project_ecosystem_pages_and_career_initiative]]. NOTE: feature-branch `git push` IS allowed for the agent here (only default-branch / API-bypass pushes auto-deny) — so push-immediately is actually available, use it.
