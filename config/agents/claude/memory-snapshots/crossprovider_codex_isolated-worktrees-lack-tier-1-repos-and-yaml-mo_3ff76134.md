---
name: crossprovider codex isolated-worktrees-lack-tier-1-repos-and-yaml-mo
description: Isolated worktrees lack tier-1 repos and yaml module
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sparse-checkouts, environment-constraints]
---

Sparse/isolated checkouts in this environment deliberately omit tier-1 sibling repositories and certain Python modules (yaml). Pre-push hooks and full test suites will fail in this configuration; record blocking dependencies without forcing workaround.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
