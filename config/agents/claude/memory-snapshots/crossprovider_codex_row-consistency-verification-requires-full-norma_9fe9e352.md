---
name: crossprovider codex row-consistency-verification-requires-full-norma
description: Row-consistency verification requires full normalized equality, not just ID matching
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [testing, data-integrity, verification, row-equality]
---

When verifying ledger/report synchronization across multiple artifacts, sort by primary key and compare all fields, not just routing IDs. Same-ID/different-field mismatches indicate undetected drift. Tests must explicitly cover this case as a failure mode to catch corruption early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
