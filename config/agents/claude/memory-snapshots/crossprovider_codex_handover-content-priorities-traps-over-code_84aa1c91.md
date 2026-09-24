---
name: crossprovider codex handover-content-priorities-traps-over-code
description: Handover content priorities: traps over code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [handoff-patterns, knowledge-transfer, operational-debt]
---

High-value handovers transfer hard-won operational traps and gotchas (CI breakage patterns, filesystem quirks, data interpretation edge cases) rather than codebase overview. The next agent can read code; it cannot rediscover that data(cost) breaks CI or that NTFS-FUSE mounts break git operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
