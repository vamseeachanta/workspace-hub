---
name: crossprovider codex large-migrations-require-dedicated-apply-commit-
description: Large migrations require dedicated apply commit and file-count restoration in rollback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [rollback, git, migration, safety]
---

Rollback plan must enforce that apply runs in a single isolated commit (not bundled with unrelated changes) and include file-count re-checks after revert to catch partial failures. Define commit boundary before apply to ensure rollback safety.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
