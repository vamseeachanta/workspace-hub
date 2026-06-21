> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_parallel_agents_shared_mutable_tool_path.md

---
name: feedback_parallel_agents_shared_mutable_tool_path
description: Parallel subagents must not share one mutable tool/script path — one agent patching it mid-run races the others. Give each its own copy or freeze it read-only.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7fadb7c-8e14-45c9-8014-2cbd970bbd6d
---

2026-06-14 (epic #3084 rollout): dispatched 4 parallel agents to apply a scaffolder script that all read from one shared path `/tmp/wh-tool/scripts/memory/scope-repo-memory.sh`. One agent discovered a bug (worktree `.git`-file guard) and PATCHED the shared script mid-run to unblock itself. The other agents had already run against the unpatched version, and a separate `basename` bug baked the worktree dir name ("wt-digitalmodel") into one repo's generated file — which slipped through because results weren't uniform.

**Why:** concurrent agents sharing a mutable file is a data race. A self-healing agent that edits the shared tool changes behavior for siblings still running. Non-determinism + inconsistent outputs that are hard to attribute.

**How to apply:**
- When fanning out agents that all invoke the same helper script/tool, either (a) freeze it: copy to a read-only path per batch and have agents treat it as immutable, or (b) give each agent its OWN copy, or (c) run the batch sequentially via a single driver script you control. The batch-2 sequential driver here was clean; batch-1 parallel-shared was not.
- ALWAYS verify each parallel agent's actual output artifact, not just its success report (subagent acceptance-metric / Write-phantom). Here a per-item `grep` for the contamination marker caught the one bad repo.
- Tool bugs found mid-rollout (worktree-incompatibility: `.git` is a FILE in linked worktrees; deriving repo identity from `basename($PATH)` instead of the origin URL) are generalizable defect classes — fix in the committed tool + add a regression test, don't just patch the scratch copy.

Related: [[feedback_amend_clobbers_parallel_branch_in_shared_checkout]], [[feedback_subagent_acceptance_metric_drives_signal_deletion]], [[feedback_subagent_write_phantom]], [[feedback_multi_agent_commit_serialization]].
