---
name: crossprovider codex codex-plan-review-failures-in-sandbox-due-to-loc
description: Codex plan-review failures in sandbox due to local-workspace retrieval unavailability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, sandbox, retrieval, environment-constraints]
---

When Codex runs in sandboxed environments, shell/REPL/MCP access to local workspace files may fail (bwrap sandbox issues); fallback attempts (shell → REPL → MCP → GitHub) exhaust before plan review can proceed. Blocker: plan artifacts must be on accessible refs or pasted verbatim for review in sandboxed runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
