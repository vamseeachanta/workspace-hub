---
name: agent-cli-delegation-operations
version: 1.0.0
category: autonomous-ai-agents
description: "Class-level Codex/Codex/delegate_task agent operations: background execution, stdin/print stalls, plugin IDs, worker patch loops, and fallback routing."
tags: [Codex, codex, agents, delegation]
---

# Agent Cli Delegation Operations

## When to Use
Use when launching or supervising autonomous CLI agents, recovering stalled Codex/Codex runs, handling delegate_task limitations, routing failed Codex lanes to Codex, or maintaining plugin identity scope.

## Class-Level Workflow
1. Prefer explicit background process tracking and absolute logs over shell-disowned runs.
2. Close stdin for Codex modes that wait for EOF; salvage Codex print stalls by checking process state and logs.
   - If a Codex background log contains only `Reading additional input from stdin...`, treat it as likely waiting for EOF or prompt delivery rather than useful progress. Re-check current `codex exec --help`, relaunch with a known-good stdin-close/input pattern, and verify output artifacts advance.
3. Poll by captured session IDs after launch; generic process lists can be empty even while known background sessions are still running. Treat `process list` as advisory, not authoritative, when session IDs are available.
4. For Gemini CLI lanes launched inside a repository, remember Gemini may auto-load `.gemini/agents/*.md`. Startup validation errors such as unsupported `permissionMode` keys can prevent useful work even while the wrapper remains alive; capture the error, run from a clean context or fix the agent definitions through a validated repo change.
5. Treat delegate_task lane limits as an orchestration constraint.
6. When a worker patches canonical skills, verify file paths and resulting content before reporting success.
7. Keep provider/agent fallback decisions evidence-based.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `Codex-delegated-issue-tree-expansion`

- Former skill demoted to `references/Codex-delegated-issue-tree-expansion.md`.
- Preserved insight: Use Codex subagents for read-only gap analysis to expand an umbrella GitHub issue into a layered tree of focused child issues, then create the issues locally and update the issue map/docs.

### `Codex-plugin-update-id-scope`

- Former skill demoted to `references/Codex-plugin-update-id-scope.md`.
- Preserved insight: Fix Codex plugin update failures caused by using the short plugin name instead of the installed plugin id and wrong scope.

### `Codex-print-stall-salvage`

- Former skill demoted to `references/Codex-print-stall-salvage.md`.
- Preserved insight: Recover delegated Codex print-mode runs that stall silently or produce partial edits in large worktrees.

### `Codex-worker-patch-loop`

- Former skill demoted to `references/Codex-worker-patch-loop.md`.
- Preserved insight: Use Codex as a delegated worker to patch canonical skills or policy files directly, then verify and iterate from the main session.

### `codex-background-burn-orchestration`

- Former skill demoted to `references/codex-background-burn-orchestration.md`.
- Preserved insight: Run quota-aware Codex usage-burn waves as useful background issue-execution lanes, including Hermes stdin-close and sandbox recovery patterns.

### `codex-background-stdin-close`

- Former skill demoted to `references/codex-background-stdin-close.md`.
- Preserved insight: Launch Codex CLI background runs in Hermes when Codex hangs at `Reading additional input from stdin...`; use explicit process stdin close and isolated worktrees.

### `codex-skill-loader-broken-symlink-recovery`

- Former skill demoted to `references/codex-skill-loader-broken-symlink-recovery.md`.
- Preserved insight: Diagnose Codex startup failures in workspace-hub caused by a broken `.Codex/skills/skills` symlink and recover without misattributing the failure to issue scope.

### `delegate-task-4-lane-workaround`

- Former skill demoted to `references/delegate-task-4-lane-workaround.md`.
- Preserved insight: Work around delegate_task batch concurrency cap when the user wants four parallel review lanes.

### `interactive-Codex-to-file-based-fallback`

- Former skill demoted to `references/interactive-Codex-to-file-based-fallback.md`.
- Preserved insight: Switch from tmux/interactive Codex to file-based Codex -p execution when interactive runs fail with upstream errors or analysis-only stalls, then verify landing from git/GitHub state.
