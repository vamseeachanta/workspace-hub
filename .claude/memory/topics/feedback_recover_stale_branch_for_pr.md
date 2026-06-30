> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-29
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_recover_stale_branch_for_pr.md

---
name: feedback_recover_stale_branch_for_pr
description: Recovering an unpushed local branch into a PR — rebase/cherry-pick onto current origin/main first; never naive-push a stale branch
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d3595eb1-9926-403a-8e08-2b56c7533826
---

When recovering an unpushed local branch (or uncommitted worktree content) into a PR in this workspace, the branch is almost always based on a **far-stale main** — local mains and feature branches here drift 100+ commits behind origin/main from multi-machine auto-sync churn (saw workspace-hub main 165 behind, `fix/statusline-codex-quota` 146 behind, llm-wiki worktree branch 20 behind, 2026-05-29).

**Why:** A naive `git push` + PR against current origin/main then shows a catastrophic diff that *deletes* all the intervening work (e.g. `git diff origin/main..HEAD` = 287 files / -81390 lines for a branch whose 3 commits only touched 20 files). The PR looks like it reverts main.

**How to apply:**
1. Check `git rev-list --left-right --count HEAD...origin/main` first — ahead is the real work, behind is the staleness.
2. Rebase onto origin/main (clean if edits are additive — llm-wiki index/log auto-merged), OR cherry-pick just the meaningful commits onto a fresh worktree branched from origin/main.
3. **Drop `chore(sync): auto-sync …` commits** — they're generated state churn (provider-kanban/scorecard JSON, `.jsonl` signals) already superseded by newer main; never put them in a PR.
4. Do the work in a `git worktree add` from origin/main so the dirty main checkout (often 1000s of churn files) stays untouched.
5. **Force-push is auto-denied** by the Claude Code mode classifier (rewrites remote history). Don't fight it — push to a NEW branch name (e.g. `<branch>-clean` or `-YYYY-MM-DD`); the old stale remote pointer is harmless. Validated llm-wiki PR #173, workspace-hub PR #2872.

Related: [[feedback_sparse_worktree_commit_trap]], [[feedback_reflog_as_ground_truth]], [[feedback_autosync_silent_pusher]], [[feedback_codex_worktree_sandbox_three_layer]].
