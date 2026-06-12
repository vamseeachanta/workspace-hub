---
name: crossprovider codex orchestrator-written-learnings-are-silently-evic
description: Orchestrator-written learnings are silently evicted without preservation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [memory, knowledge-loss, eviction, WRK-1105]
---

WRK-1105 core finding: WRK summaries written manually to MEMORY.md by orchestrator accumulate at 146/200 lines with ~25 archived entries. compact-memory.py silently evicts done-WRK entries on line overflow with zero preservation. Knowledge is permanently lost. Need automatic capture at archive time into a queryable knowledge-base.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
