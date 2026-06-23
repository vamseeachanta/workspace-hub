---
name: crossprovider codex parallel-repo-exploration-handoffs-require-durab
description: Parallel repo exploration handoffs require durable locations and coordination artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [parallel-sessions, coordination, handoff-pattern]
---

Handoff files in /tmp are lost on session close; findings must be written to git-tracked memory or coordination paths accessible to parallel sessions. Include relocation logs, negative evidence (e.g. 'SubseaIQ NOT found in these tables'), and schema/header samples to save parallel session exploration overhead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
