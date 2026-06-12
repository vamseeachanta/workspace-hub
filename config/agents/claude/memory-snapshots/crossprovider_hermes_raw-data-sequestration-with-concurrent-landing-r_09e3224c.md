---
name: crossprovider hermes raw-data-sequestration-with-concurrent-landing-r
description: Raw data sequestration with concurrent-landing race prevention via live-tree invariants
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, concurrency, raw-data-boundary]
---

Raw stays in `/mnt/ace`, wiki receives only summaries/metadata after approval (#2540 epic). Overview-count races (e.g., #2638/#2639) need re-derive-at-execution-time contracts with live-tree count invariants, not static snapshot checks or vague "stale-claim" heuristics.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
