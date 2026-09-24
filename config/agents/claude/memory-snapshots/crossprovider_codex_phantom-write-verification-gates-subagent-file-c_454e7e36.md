---
name: crossprovider codex phantom-write-verification-gates-subagent-file-c
description: Phantom write verification gates subagent file-creation claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subagent-coordination, file-verification]
---

When subagents report file creation success, the main session must verify by reading the file (or `ls` for existence) before trusting the claim. Subagent `Write` tool success does not guarantee the file landed in the shared worktree, especially under resource contention or transaction isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
