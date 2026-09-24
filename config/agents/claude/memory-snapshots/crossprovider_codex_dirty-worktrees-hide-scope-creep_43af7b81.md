---
name: crossprovider codex dirty-worktrees-hide-scope-creep
description: Dirty worktrees hide scope creep
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hygiene, scope-management, review]
---

When reviewing for scope contamination, check whether unrelated issues are also modified in the same commits. Dirty tracked files (e.g., matrix/test artifacts) can indicate multiple in-flight changes that complicate isolation and rollback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
