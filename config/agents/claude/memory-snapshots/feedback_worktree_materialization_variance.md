---
name: worktree-materialization-variance-workspace-hub
description: "workspace-hub git worktree add materialization is indeterminate — 17 min one run, 1h+ stalled another, depending on parallel agent I/O load"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 000d04a3-532a-4959-becb-59b1f1349fb3
---

`git worktree add --detach <path> HEAD` on workspace-hub (~19455 tracked files) completes in 17 minutes under a clean machine, but stalls past 1+ hour when 200+ parallel agent processes (Hermes workers, parallel Codex agent sessions) are competing for I/O. The variance is multiplicative, not linear.

**Why:** Discovered 2026-05-22 attempting two consecutive worktree-isolated push retries. First attempt: 17 min materialization completed; rebase hit JSONL conflict; failed but worktree did materialize. Second attempt minutes later under same machine load: worktree directory never appeared after 60+ min, materialization process was alive but making no observable disk progress. Killed via SIGTERM with zero state on disk. The 260 Hermes workers spawned by the earlier kanban load + parallel agent worktrees (issue-2747-ledger-codex, issue-2746-private-wiki-claude, etc.) saturated I/O.

**How to apply:**
- Worktree isolation is NOT a reliable push-recovery path on workspace-hub when other agents are running. Per [[feedback_worktree_isolation_large_repo_cost]] memory says reserve for commit/push agents, but even those time out here.
- Preferred recovery for "push my commit when local main is divergent and dirty":
  1. `git push origin <my-sha>:refs/heads/<feature-branch>` — surgical, no rebase, no WT requirement.
  2. PR + merge via GitHub UI (handles JSONL union-merge server-side).
- If worktree IS the only path: kill the in-flight hermes workers first (`hermes gateway stop` + worker pkill — requires sudo for gateway service unit), wait for the system to quiesce, THEN start worktree.
- Always run a quick sanity poll 5 min in: if the worktree dir doesn't exist yet at 5 min, the materialization is likely stalled and should be killed rather than waited on.

Related: [[feedback_worktree_isolation_large_repo_cost]], [[autostash-lock-race-workspace-hub]].
