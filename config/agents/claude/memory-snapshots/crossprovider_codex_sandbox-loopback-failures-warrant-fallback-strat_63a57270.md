---
name: crossprovider codex sandbox-loopback-failures-warrant-fallback-strat
description: Sandbox loopback failures warrant fallback strategies, not retry loops
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sandbox, fallback, tooling]
---

`bwrap: loopback: Failed RTM_NEWADDR` errors are environment/container-specific and persist across retries. Codex sessions should fall back to GitHub connector or read-only MCP rather than retry local execution. Fallback paths (connector diffs, wiki inspection) complete when local shell is blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
