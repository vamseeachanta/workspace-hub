---
name: crossprovider gemini race-safe-file-claiming-uses-pre-check-atomic-re
description: Race-safe file claiming uses pre-check + atomic rename, not locks as enforcement
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, filesystem-atomicity, work-queue]
---

POSIX `rename(2)` is atomic on same filesystem; a pre-check-then-move pattern is safe against concurrent claims. Lock files work as immutable audit trails (pid/hostname/timestamp/status transitions) but not as the primary enforcement mechanism.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
