---
name: crossprovider gemini exit-code-4-reserved-for-concurrent-work-queue-l
description: Exit code 4 reserved for concurrent work queue lock conflicts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, error-handling, exit-codes]
---

Specific exit codes should map to specific gate failure types: 1, 2, 3 for other gate failures; 4 specifically for concurrent WRK claims when two sessions attempt to claim the same item simultaneously. This enables automated retry logic that respects lock contention.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
