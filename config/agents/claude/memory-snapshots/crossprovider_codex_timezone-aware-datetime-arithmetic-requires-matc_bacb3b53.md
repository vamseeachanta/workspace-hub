---
name: crossprovider codex timezone-aware-datetime-arithmetic-requires-matc
description: Timezone-aware datetime arithmetic requires matching timezone awareness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [datetime, timezone, error-handling, data-pipelines]
---

Subtracting a naive datetime from timezone-aware (or vice versa) raises `TypeError`. When parsing user-supplied timestamps with `datetime.fromisoformat()`, wrap in try-except, normalize naive values to UTC, or skip invalid entries rather than crashing the entire operation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
