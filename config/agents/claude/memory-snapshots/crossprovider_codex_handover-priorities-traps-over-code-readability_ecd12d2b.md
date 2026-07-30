---
name: crossprovider codex handover-priorities-traps-over-code-readability
description: Handover priorities: traps over code readability
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [handover, knowledge-transfer, documentation]
---

Handovers should lead with hard-won gotchas and tool-specific quirks (e.g., git stalls on NTFS-FUSE, data(cost): breaks CI lint, specific package version conflicts). Next agent can read code; it cannot rediscover these traps. Separate a dedicated gotchas section.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
