---
name: crossprovider codex manifest-drift-reporting-must-be-computed-post-u
description: Manifest drift reporting must be computed post-update
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [reporting, state, ordering, ux]
---

When `--update-counts` fixes manifest, it still emits 'drift(s) found (run --update-counts to fix)' based on pre-update state. Recompute drift after update or suppress pre-update report when repair succeeds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
