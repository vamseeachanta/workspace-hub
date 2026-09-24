---
name: crossprovider codex handover-design-transfer-traps-not-code
description: Handover design: transfer traps, not code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [handoff, documentation, cross-agent-work]
---

A handover's real value is documenting hard-won gotchas—the traps that aren't rediscoverable from reading code alone (e.g., 'data(cost) breaks CI', 'NTFS-FUSE mount stalls git', 'not_public row is a finding'). Pin state counts to post-merge values and explicitly flag unmerged branches to prevent silent discrepancies when the next agent reads it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
