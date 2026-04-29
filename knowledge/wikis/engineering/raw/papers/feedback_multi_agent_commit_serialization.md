> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_multi_agent_commit_serialization.md

---
name: Serialize commit phase when parallel agents touch shared index files
description: Parallel agents editing the same index/README/shared file (e.g., docs/plans/README.md) race on git index lock; commits merge into whichever agent won the race, losing per-plan attribution. Serialize the commit phase or use per-agent worktrees
type: feedback
originSessionId: 9b439b61-1bc0-4c85-b9a9-727564b48494
---
When dispatching multiple agents in parallel that all touch a shared file (commonly `docs/plans/README.md`, but also `MEMORY.md`, `.planning/intel/*`, any tracker file), their commit phases collide:
- Agent A stages its plan file + README row edit, runs pre-commit hook
- Agent B stages its plan file + README row edit concurrently
- Both hit `.git/index.lock` — one wins, one retries with the OTHER agent's staged work already in the index
- Result: Agent A's commit may contain Agent B's README edit and vice versa; "docs(plans): #X" commits end up containing other plans' content

**Observed 2026-04-20:** Wave 3 dispatched 3 parallel plan-revision agents. Final state on main: commit `298d2d729` ("#2367 v2") contained content from #2391 v2 and #2407 triage. A dedicated `docs(plans): #2391 v2` commit never existed. Content was correct on main; `git blame` and audit trail were degraded.

**How to avoid:**

1. **Preferred — serialize the commit phase.** Let each agent do its resource-intel + edits + Write/Edit calls in parallel, but have a single dispatcher-level step run `git add -A && git commit -m <per-plan-message>` per plan, in sequence. The inter-commit delay is <2s each — still overall-parallel for the expensive edit phase.

2. **Alternative — per-agent worktrees.** `git worktree add .claude/worktrees/agent-<N> main` gives each agent an isolated working tree with its own index. Commits land cleanly per agent. Requires worktree cleanup.

3. **Retry with lock-busting in the prompt:** instruct each agent to `rm .git/index.lock` only after verifying no `git` process is actually running (`pgrep git`), then retry. Brittle; avoid.

**How to apply:**

- Before dispatching N parallel agents where ANY of them will `git commit`, check whether they all touch the same index file.
- If yes: restructure — either (a) have agents STAGE but not COMMIT (return diff as output, dispatcher commits serially) or (b) use worktrees.
- If no: parallel commits are fine.

**Signal that serialization is needed:** if your parallel dispatch involves ≥2 agents all creating a new `docs/plans/*.md` file, they'll all edit the Plan Index in `docs/plans/README.md` — serialize.
