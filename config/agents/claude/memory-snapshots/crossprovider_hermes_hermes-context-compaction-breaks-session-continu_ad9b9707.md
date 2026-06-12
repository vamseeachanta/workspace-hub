---
name: crossprovider hermes hermes-context-compaction-breaks-session-continu
description: Hermes context compaction breaks session continuity across reboots
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-limits, context-management, session-continuity]
---

Sessions report "Summary generation was unavailable" frequently, leaving gaps between tool-call limits and actual summaries. Threads resume with only compacted context that includes active task list but lose detailed prior work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
