---
name: crossprovider codex parallel-write-risk-in-shared-checkouts-snapshot
description: Parallel-write risk in shared checkouts; snapshot and document divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, shared-workspace, coordination]
---

Sibling worktrees and concurrent agents can modify files during read-only inspection (e.g., test files appearing mid-scan). Take explicit state snapshots before and after review work, and document unexpected changes (modified files, new untracked artifacts) as evidence of parallel activity rather than silently merging observations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
