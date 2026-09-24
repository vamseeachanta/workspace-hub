---
name: crossprovider codex tracked-generated-state-paths-for-agents-and-too
description: Tracked generated state paths for agents and tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generated-state, git-hygiene, memory-management]
---

.claude/memory/**, config/agents/*/MEMORY.runtime.md, logs/orchestrator/*/*.jsonl, state/reflect-history/*.md, state/session-signals/*.jsonl are repo-tracked durable state. Auto-sync may move HEAD during analysis; verify with reflog for ground truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
