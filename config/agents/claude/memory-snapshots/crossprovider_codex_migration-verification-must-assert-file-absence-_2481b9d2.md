---
name: crossprovider codex migration-verification-must-assert-file-absence-
description: Migration verification must assert file absence in source after copy, not just presence in target
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, testing, completeness, safety]
---

Early verification only checked pointer README existed; partial cleanup (files not deleted from local specs/) passed unnoticed. Add explicit `find ... ! -name 'README.md'` assertions to catch incomplete migrations where residue remains in source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
