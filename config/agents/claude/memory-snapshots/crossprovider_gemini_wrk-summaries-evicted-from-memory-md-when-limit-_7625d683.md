---
name: crossprovider gemini wrk-summaries-evicted-from-memory-md-when-limit-
description: WRK summaries evicted from MEMORY.md when limit hit
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [memory-management, wrk-workflow, knowledge-persistence]
---

Auto-memory orchestrator writes WRK completion summaries to MEMORY.md manually. compact-memory.py evicts them when file hits line limit. Without capture script at archive time, these learnings are permanently lost. Archive-time capture + queryable knowledge base prevents eviction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
