---
name: crossprovider codex committed-client-data-leak-risk-in-sensitive-rep
description: Committed client-data leak risk in sensitive repos
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, data-governance, pre-commit-guard]
---

Repositories containing real client/field names (e.g., digitalmodel) require guards to prevent accidental publicization in PRs, commits, or issues. Use path-level `--added mode` absolute-path checks in pre-commit hooks to block new machine/client paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
