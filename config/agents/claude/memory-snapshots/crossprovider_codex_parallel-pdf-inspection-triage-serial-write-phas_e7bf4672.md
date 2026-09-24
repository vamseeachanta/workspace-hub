---
name: crossprovider codex parallel-pdf-inspection-triage-serial-write-phas
description: Parallel PDF inspection triage + serial write phase enables safe scaling without races
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, serialization, scale, workflow]
---

Dispatch read-only PDF classification and dedupe checks across parallel subagents (independent PDF groups). Converge to serial write phase for new pages, augmentations, and skip rows, scoped to explicit chunks (e.g., 'chunk 0010' with exact document list). Parallel latency reduction + serial write discipline = safe at scale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
