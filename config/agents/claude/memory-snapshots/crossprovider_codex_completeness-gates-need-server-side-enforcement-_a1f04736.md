---
name: crossprovider codex completeness-gates-need-server-side-enforcement-
description: Completeness gates need server-side enforcement to actually block closure
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [enforcement, completeness-gate, github-api]
---

Local pre-flight checks (#744 plan) are advisory; GitHub API and UI closure paths bypass them. Enforced gates require `.github/workflows/` Actions or MCP hooks that intercept `gh issue close` or POST requests. Without server-side enforcement, closure is not actually blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
