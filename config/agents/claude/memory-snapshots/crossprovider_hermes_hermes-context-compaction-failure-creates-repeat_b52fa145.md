---
name: crossprovider hermes hermes-context-compaction-failure-creates-repeat
description: Hermes context compaction failure creates repeated-work antipattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-management, session-failure]
---

When context compaction reports 'Summary generation was unavailable,' sessions restart identical tasks (observed: #2760 restarted 8+ times in a row, sessions 212248–213525). This failure mode should trigger fallback to persistent task tracking and explicit handoff detection.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
