---
name: crossprovider codex shell-sandbox-failure-with-github-mcp-fallback
description: Shell sandbox failure with GitHub MCP fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment-quirk, codex, fallback-pattern]
---

When Codex sessions encounter shell startup failure (`bwrap: loopback: Failed RTM_NEWADDR`), GitHub connector MCP remains functional for read-only operations. Use GitHub API to query issues, check markers, and inspect repo state when local shell execution is unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
