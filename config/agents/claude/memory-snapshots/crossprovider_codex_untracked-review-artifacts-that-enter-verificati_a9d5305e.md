---
name: crossprovider codex untracked-review-artifacts-that-enter-verificati
description: Untracked review artifacts that enter verification set must be accounted for in r2
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, verification]
---

If r1 identifies file-paths that should be scanned and those files exist locally (e.g., untracked review artifacts), r2 must include them. Treating r2 as 'recheck r1 blockers' can miss scan targets that became relevant after r1.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
