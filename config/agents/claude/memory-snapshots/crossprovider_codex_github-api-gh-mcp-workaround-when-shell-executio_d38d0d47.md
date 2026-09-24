---
name: crossprovider codex github-api-gh-mcp-workaround-when-shell-executio
description: GitHub API (gh/MCP) workaround when shell execution is sandboxed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sandbox, github-connector, workaround]
---

If local bash is blocked by sandbox constraints (bwrap loopback issues), GitHub connector (gh MCP tool) can read/write issues, branches, and comments without needing shell execution. Useful for unblocking progress when local git/bash is unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
