> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_parallel_agent_write_only_pattern.md

---
name: Parallel agent dispatch — write-only + main-session serial commits
description: Dispatching 3-5 parallel agents that write files only (no commits) then having main session serialize commits avoids git-lock races without needing worktrees for every agent
type: feedback
originSessionId: e04329da-9917-4fcf-a605-7fed457336e0
---
When dispatching parallel agents for independent research/drafting tasks, instruct agents to **write files only — do NOT commit or push**. Main session then stages and commits each agent's output serially.

**Why:** Memory `feedback_multi_agent_commit_serialization.md` warns that parallel agents racing on shared git lock produce index corruption. Full worktree isolation works but adds merge-back overhead. For most agent tasks (research reports, plan drafts, scoping analyses), the output is 1-3 new files with no cross-agent conflicts. Write-only + serial commit avoids both the race AND the worktree merge step.

Validated pattern observed 2026-04-21 wave 2: 5 agents produced 10 new files + 2 revised plans across `docs/plans/`, `scripts/review/results/`, and `.planning/quick/`. Main session batch-committed in 1-3 commits after all agents completed. Zero git-lock contention.

**How to apply:**
1. Agent prompts must explicitly state: "Do NOT commit or push. Do NOT apply GitHub labels. Main session serializes commits after your completion."
2. Agents working on disjoint file paths can run concurrently without isolation.
3. When agents need to dispatch external review providers (Codex/Gemini) that require pushed artifacts, defer dispatch to main session. Agents generate Claude self-reviews inline; main session pushes + dispatches cross-provider reviews serially.
4. Before main-session commit, run `git diff --cached --name-only` — verify only agent outputs are staged. Other sessions' auto-staged files can pollute.
5. If agents must touch the same file (rare), use `isolation: worktree` for those specific agents only.
