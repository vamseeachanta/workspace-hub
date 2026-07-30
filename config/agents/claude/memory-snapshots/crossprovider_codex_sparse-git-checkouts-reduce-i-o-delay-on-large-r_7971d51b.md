---
name: crossprovider codex sparse-git-checkouts-reduce-i-o-delay-on-large-r
description: Sparse Git checkouts reduce I/O delay on large repositories
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, performance, filesystem]
---

Use `git sparse-checkout set` with exact path filters to avoid materializing unrelated corpus files. On slow or network-mounted filesystems, sparse-index mode significantly reduces checkout time and Git metadata operation latency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
