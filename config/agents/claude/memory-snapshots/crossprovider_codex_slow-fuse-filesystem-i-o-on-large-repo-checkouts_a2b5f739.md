---
name: crossprovider codex slow-fuse-filesystem-i-o-on-large-repo-checkouts
description: Slow FUSE filesystem I/O on large repo checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, filesystem, performance, infrastructure]
---

Full git fast-forward on large repositories via FUSE (e.g., workspace-hub across ~33K files) can trigger slow metadata I/O and orphan git processes. Use bounded partial clone (--filter=blob:none) and lower-I/O update paths. Reconfirm HEAD and verify no stale processes remain before proceeding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
