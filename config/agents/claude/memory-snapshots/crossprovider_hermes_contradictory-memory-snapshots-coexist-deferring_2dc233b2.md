---
name: crossprovider hermes contradictory-memory-snapshots-coexist-deferring
description: Contradictory memory snapshots coexist, deferring policy to runtime load order
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory, architecture-decision, conflict-resolution]
---

Repo contains both 'llm-wiki stays embedded' and 'llm-wiki spunout' decisions in memory snapshots. Policy is determined by which snapshot loads, not recorded decision, creating silent enforcement conflict.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
