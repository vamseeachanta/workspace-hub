---
name: crossprovider codex portable-agent-scope-workers-vs-orchestrators
description: Portable agent scope: workers vs. orchestrators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [agents, portability, architecture-decision]
---

Repo's SOUL materializer pattern is already portable (define-once, render per-provider). Extending to agent definitions: workers (bounded tasks) can be portable, but orchestrators are structurally Claude-only (slash commands, Task delegation). Extend existing patterns rather than invent parallel infrastructure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
