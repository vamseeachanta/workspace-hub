---
name: crossprovider hermes git-reset-hard-as-exception-rollback-deletes-unr
description: git reset --hard as exception rollback deletes unrelated work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-safety, rollback-pattern, destructive-operation]
---

Using `git reset --hard <before>` as a rollback in exception handlers silently discards unrelated tracked changes if preflight checks allow them. Safer pattern: backup file contents before modifications, restore only owned paths on exception, or fail closed if any non-owned dirty tracked files exist.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
