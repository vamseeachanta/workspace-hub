> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_worktree_gitlink_pollution.md

---
name: Parallel worktree workflows can pollute commits with submodule gitlinks
description: When multiple git worktrees are siblings under .claude/worktrees/, `git add` in one can pick up others as 160000 gitlinks; ensure .gitignore covers the worktree dir
type: feedback
originSessionId: 7b96f09a-c799-4575-8253-53a74702ec34
---
When agents run in parallel inside `.claude/worktrees/agent-*` worktrees and any of them does `git add -A` or `git add .`, git treats each sibling worktree as a submodule candidate (it sees `.git` metadata inside them) and records them as `160000 commit <sha>` gitlinks in the index — bypassing .gitignore entirely. These gitlinks then get carried into commits and can ride along through squash-merges into main.

**Why:** Discovered on worldenergydata 2026-04-16 when the first squash-merge of a parallel-agent PR (#295) brought 12 sibling worktree entries into main. Cleanup commit `d45db93` untracked them and added `.claude/worktrees/` to `.gitignore`. The original handoff had claimed worktrees were gitignored — they were not.

**How to apply:**
- Before running parallel-agent workflows in any repo, verify `.claude/worktrees/` (or the analogous directory) is explicitly in `.gitignore`. `.gitignore` only blocks *new* entries — already-indexed gitlinks need `git rm --cached -r` to untrack.
- After the first merge from a parallel-agent PR set, spot-check `git ls-tree HEAD .claude/worktrees/` on main. If it returns lines, run the `rm --cached` + `.gitignore` fix before merging more PRs, or each merge will re-pollute.
- The defensive fix is cheap: one commit, one line in `.gitignore`. Do it preemptively when setting up a new repo for parallel-worktree work.
