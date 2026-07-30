---
name: crossprovider codex scope-requires-bounded-enumeration-not-wildcards
description: Scope requires bounded enumeration, not wildcards
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [planning, scope, verification]
---

Claims like "covers /mnt/ace/*/data" are not verifiable; must define explicit parent paths, symlink behavior, permission/error handling, ordering, and determinism. Wildcards hide scope boundary decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
