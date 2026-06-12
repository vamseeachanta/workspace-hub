---
name: crossprovider codex stage-isolation-prevents-context-compaction-in-l
description: Stage-isolation prevents context compaction in long WRK conversations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [context-management, wrk-lifecycle, conversation-design]
---

Long conversations compress hard-stop instructions away mid-session, causing context rot where earlier stage noise pollutes later stages. Use isolated stage starts with fresh context + previous-stage artifacts as entry data, not conversation history. Each stage starts clean, and human gates become natural checkpoints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
