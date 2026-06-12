---
name: crossprovider codex nested-claude-cli-invocation-blocked-in-managed-
description: Nested Claude CLI invocation blocked in managed sessions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [platform-constraint, claude-runtime, ensemble-planning]
---

Running `claude -p` from within an active Claude Code session fails silently; the 'independent Claude agents' pattern for ensemble planning cannot be implemented via local CLI recursion. Use Task tool with subagent_type for true process isolation instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
