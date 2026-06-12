---
name: crossprovider hermes plan-gated-workflow-embedding-in-parallel-dispat
description: Plan-gated workflow embedding in parallel dispatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, parallel-safety, enforcement]
---

Embed plan-gate checks directly into task prompts (explicit status:plan-approved requirement) and forbid self-approval. Before dispatch, compute file-boundary contention map to ensure zero same-file overlap across parallel tasks. Document interdependencies upfront (e.g., #2060 must land before #2058 if both touch benchmarks.py).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
