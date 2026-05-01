> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_isolated_clone_dispatch_race.md

---
name: Isolated-clone dispatch race
description: Subagent dispatched to execute an approved issue in an isolated clone can land on top of concurrent main-workspace session; must detect landed work and abort before duplicating
type: feedback
originSessionId: 9a781448-5a8c-47ef-a9c1-b8729f1b4a6d
---
Subagent execution prompts that target a dedicated isolated clone (`/mnt/local-analysis/worktrees/*-exec-clone`) assume the clone is the only active execution lane for the approved issue. This assumption is unreliable: a concurrent main-workspace session can also be executing the same approved issue and finish first.

Observed on 2026-04-23 for #2460:
- Dispatcher created isolated clone at `/mnt/local-analysis/worktrees/workspace-hub-2460-exec-clone`, announced `issue-2460-contract-exec` branch intent, posted 20:47 UTC "Execution started" comment on #2460.
- A parallel main-workspace session on `integration/runbook-main-compatible` committed equivalent implementation at `8e7b65a3d` around the same clock minute, posted 20:50 UTC "landed" comment, and the issue was closed before the isolated-clone subagent could start implementation.
- Isolated-clone subagent session was sandboxed to `/mnt/local-analysis/workspace-hub` (write access to the clone path was blocked), so it could not write files into the clone anyway.

**Why:** Subagent dispatches and ambient sessions share the same approved GitHub issue and the same remote, so whoever commits first wins. Isolation guarantees don't hold across clone boundaries when both lanes target the same issue.

**How to apply:**
- Subagent executing an approved issue in an isolated clone MUST check, before any write, whether: (a) the live GitHub issue is already closed, (b) the issue has a "landed" comment newer than the dispatch timestamp, and (c) the main workspace has a commit matching the expected acceptance criteria.
- If any of these is true, abort: do not create a new branch, do not push, do not post another comment.
- Also flag this to the dispatcher as `blocked: duplicate-parallel-completion` with references to the winning commit/comment.
- Dispatcher pattern to consider in the future: hold the `status:plan-approved` label behind a single-assignee lock, or have the dispatcher post an "execution lock" comment that the losing lane can honor.
