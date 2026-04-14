> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_check_parallel_work.md

---
name: Check for parallel work before acting
description: Always check for in-progress GSD phases, worktrees, or recent file modifications before starting or suggesting work
type: feedback
---

Before starting any GSD workflow or suggesting next steps, check for signs of parallel work in other terminals:
- Recent file modifications in `.planning/phases/` (within last ~30 min)
- Active git worktrees (`git worktree list`)
- Untracked/modified `.planning/` files in git status
- Missing PLAN.md but fresh RESEARCH.md = planner likely running

**Why:** User runs multiple Claude Code sessions in parallel. Suggesting or starting work that's already in progress wastes time and causes conflicts.

**How to apply:** At session start and before any `/gsd:*` action, do a quick scan of `.planning/` timestamps and worktrees. If something looks actively in-flight, flag it rather than proceeding.

**Partial automation (2026-03-31):** WIP label claim/release added to `whats-next` (commit `cd01e6aa`) — prevents cross-machine issue clashing by labeling issues as claimed. This reduces but doesn't eliminate the need for manual parallel-work checks.
