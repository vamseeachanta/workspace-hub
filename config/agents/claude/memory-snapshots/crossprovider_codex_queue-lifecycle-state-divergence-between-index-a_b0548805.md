---
name: crossprovider codex queue-lifecycle-state-divergence-between-index-a
description: Queue lifecycle state divergence between index and disk requires explicit git staging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-state, work-queue, file-management]
---

Moving items (working/WRK-673.md → done/WRK-673.md) creates untracked copies and tracked deletes; use explicit git add/mv or close-item.sh logic to stage as rename, then regenerate INDEX.md. Implicit moves silently lose history and confuse validators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
