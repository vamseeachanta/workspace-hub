---
name: crossprovider codex branch-cleanup-audits-must-account-for-moved-ren
description: Branch cleanup audits must account for moved/renamed files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [git, branch-cleanup, content-equivalence]
---

Content-equivalence checks that rely on exact paths will report false 'unique content' when equivalent code has moved or been renamed. Audit must directly compare content against origin/main, including checking for relocated or renamed equivalents. Byte-identity in a different location is still safe to delete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
