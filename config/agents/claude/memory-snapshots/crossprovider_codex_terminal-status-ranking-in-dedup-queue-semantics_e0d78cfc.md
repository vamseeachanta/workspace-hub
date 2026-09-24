---
name: crossprovider codex terminal-status-ranking-in-dedup-queue-semantics
description: Terminal status ranking in dedup queue semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, queue-semantics, state-machine, terminal-status]
---

When a row has multiple parse attempts (provisional/deferred/verified/rejected), rank determines which wins in dedup. Example: verified(3) > rejected(2) > deferred(1) > provisional. Must be explicit in the data structure to prevent re-selection of rejected/deferred rows while ensuring verified always overwrites lower-rank duplicates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
