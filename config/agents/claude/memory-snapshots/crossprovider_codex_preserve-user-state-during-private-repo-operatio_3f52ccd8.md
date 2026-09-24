---
name: crossprovider codex preserve-user-state-during-private-repo-operatio
description: Preserve user state during private repo operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, private-repos, operational-safety]
---

When pulling/cloning private repos with dirty working trees, use low-I/O update paths and preserve untracked files (e.g., user notes). Avoid merge-style pulls and force-clean operations that discard user state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
