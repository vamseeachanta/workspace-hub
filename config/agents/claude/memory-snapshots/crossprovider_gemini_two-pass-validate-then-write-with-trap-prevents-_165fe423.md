---
name: crossprovider gemini two-pass-validate-then-write-with-trap-prevents-
description: Two-pass validate-then-write with trap prevents orphans
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [atomicity, error-handling, bash]
---

Pass 1: allocate IDs, validate all dependencies, collect sentinels in array. If any validation fails, trap cleanup deletes sentinels before exit. Pass 2: write all files (no validation errors reachable). Disarm trap before Pass 2 completes. Ensures atomicity: either all succeed or all rollback.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
