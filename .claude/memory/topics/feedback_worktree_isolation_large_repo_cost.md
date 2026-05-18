> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_worktree_isolation_large_repo_cost.md

---
name: Worktree-isolation Agent mode is too slow on workspace-hub-sized repos
description: Spawning Agent with isolation=worktree triggers a full 33,325-file checkout that exceeds tool timeout 60% of the time on workspace-hub. Default to write-only-shared mode for parallel agent dispatch; reserve worktree-isolation for agents that genuinely need git index isolation.
type: feedback
originSessionId: bdc56a6b-6852-40d5-b0af-66c0a71a60de
---
The Agent tool's `isolation: worktree` parameter creates a fresh git worktree before the agent starts. For large repos this is unworkable — workspace-hub has 33,325 tracked files and the checkout times out partway through 60% of the time.

**Why:** Observed 2026-05-02 dispatching 5 parallel /whats-next plan-drafting agents — 3 of 5 failed at "Failed to create worktree" with `Updating files: 82% (27327/33325)` truncation. The 2 that succeeded then paid further friction: one wrote its plan to the main checkout instead of the worktree (anchor drift, recovered by copying), and one's session-sync auto-merged the worktree branch back to main with a misleading commit message ("plan(#2479)" containing the #2523 file too).

**How to apply:**

1. **Default for parallel agent dispatch on workspace-hub: `write-only-shared`** mode — agents share `/mnt/local-analysis/workspace-hub`, write only to unique paths, and main session batch-commits. See `feedback_parallel_agent_write_only_pattern`.
2. **Use `isolation: worktree` only when** the agent must run `git commit`/`git push` itself, or must check out a different branch, or runs commands that mutate the index. For pure file-drafting + label-mutation work, write-only-shared is strictly faster and simpler.
3. **If you do use worktree isolation**, expect: the worktree dir at `.claude/worktrees/agent-<id>/`, `git worktree list` showing it as `locked`, post-completion the dir may persist or be GC'd by harness, and the branch on origin uses the auto-generated `worktree-agent-<id>` naming.
4. **Anchor drift mitigation** — when an agent does run in worktree mode, the prompt MUST explicitly tell it to `cd` to the worktree path before any file work, and to verify with `pwd` before writing. Per `.claude/skills/coordination/issue-planning-mode/SKILL.md:48`, "explicitly anchor the repo/worktree path... do not assume the child agent stayed in the requested worktree."
5. **Sparse-checkout-aware isolation is not currently available** in the Agent tool — there's no `isolation: sparse-worktree` option. If you need both isolation and avoid the full-checkout cost, use a manually-prepared worktree at a known path and tell the agent to use it, rather than relying on the tool's auto-isolation.

**Anti-pattern to avoid:** Dispatching 5 agents with `isolation: worktree` against workspace-hub and assuming they all succeed. Always check the tool result for "Failed to create worktree" and re-dispatch failures in write-only-shared mode.
