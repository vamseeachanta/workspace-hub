---
name: crossprovider codex silent-auto-sync-commits-can-occur-during-sessio
description: Silent auto-sync commits can occur during session execution when uncommitted state is required
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, automation, hazard]
---

Repos with auto-sync enabled may silently create commits during normal work without explicit user action. Detect via `git reflog` and safely revert with `git reset --mixed <prior-commit>` to preserve working-tree changes while restoring the uncommitted-state requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
