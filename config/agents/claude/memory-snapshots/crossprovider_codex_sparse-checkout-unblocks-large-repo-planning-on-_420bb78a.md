---
name: crossprovider codex sparse-checkout-unblocks-large-repo-planning-on-
description: Sparse checkout unblocks large-repo planning on slow/dirty canonical branches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, performance, workflow]
---

Use `git sparse-checkout` to materialize only docs/planning paths when canonical checkout times out (60%+ risk on large repos). Isolates planning work from implementation paths and avoids thrashing slow mounts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
