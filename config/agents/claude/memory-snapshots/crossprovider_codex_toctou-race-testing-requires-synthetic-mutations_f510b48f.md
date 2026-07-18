---
name: crossprovider codex toctou-race-testing-requires-synthetic-mutations
description: TOCTOU race testing requires synthetic mutations during window, not boundary checks alone
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [concurrency-testing, race-conditions, tdd]
---

Testing verify–count–publish races by checking only pre/post state misses the actual window. Add synthetic deletions/modifications to the regress suite that occur between the verify step and final emission. Prove the fix rejects mid-flight mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
