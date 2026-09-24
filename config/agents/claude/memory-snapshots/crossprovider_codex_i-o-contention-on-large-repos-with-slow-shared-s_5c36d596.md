---
name: crossprovider codex i-o-contention-on-large-repos-with-slow-shared-s
description: I/O contention on large repos with slow shared storage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, io-contention, large-repos]
---

Direct reconciliation scans on large repos mounted on slow shared storage will stall on concurrent reads (e.g., `git status` on sibling checkouts). Defer to already-running scheduled audits rather than launching competing scans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
