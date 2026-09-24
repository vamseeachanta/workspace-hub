---
name: crossprovider codex sandbox-environment-fallback-to-github-connector
description: Sandbox environment fallback to GitHub connector on shell blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operations, environment, fallback-pattern]
---

When local shell execution is blocked at process start (e.g., `bwrap: loopback: Failed RTM_NEWADDR`), GitHub connector reads still work. Switch to MCP-based inspection and report blockers explicitly rather than pretending local verification happened.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
