---
name: crossprovider codex repository-memory-file-absence-with-agents-rules
description: Repository memory file absence with AGENTS rules fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operational-pattern, memory-management, agent-config]
---

When repo-specified agent memory files (e.g., `config/agents/codex/MEMORY.runtime.md`) are absent, proceed with the supplied AGENTS.md rules and local git evidence rather than blocking. Note this state in handoffs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
