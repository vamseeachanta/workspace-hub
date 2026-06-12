---
name: crossprovider gemini dry-run-manifest-capture-with-checksums-enables-
description: Dry-run manifest capture with checksums enables rollback
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, verification, traceability]
---

Before apply, capture dry-run output, source/target SHA256 checksums, file inventories, and collision checks. Verified approach: dry-run log hash, source file count, parity check post-apply. Enables rapid rollback decision (stop if any check fails before apply) and post-apply verification (diff checksums with path normalization).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
