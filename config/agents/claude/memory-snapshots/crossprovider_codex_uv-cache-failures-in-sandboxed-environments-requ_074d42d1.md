---
name: crossprovider codex uv-cache-failures-in-sandboxed-environments-requ
description: Uv cache failures in sandboxed environments require escalation, not invocation changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, sandboxing, uv, debugging]
---

When `uv run` fails in a sandboxed/read-only environment with a cache-write error, the correct response is to escalate and retry outside the sandbox, not to change the invocation. The invocation is correct; the environment is the constraint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
