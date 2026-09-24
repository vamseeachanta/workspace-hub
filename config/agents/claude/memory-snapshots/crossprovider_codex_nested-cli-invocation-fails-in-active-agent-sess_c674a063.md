---
name: crossprovider codex nested-cli-invocation-fails-in-active-agent-sess
description: Nested CLI invocation fails in active agent session
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell, agents, architecture, cli]
---

Invoking provider CLIs (claude -p, codex exec, gemini -p) recursively within an active agent session fails. This blocks multi-agent orchestration patterns that rely on local process spawning. Use Task/subagent primitives for independent agent contexts instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
