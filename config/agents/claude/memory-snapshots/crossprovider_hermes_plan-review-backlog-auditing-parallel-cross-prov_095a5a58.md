---
name: crossprovider hermes plan-review-backlog-auditing-parallel-cross-prov
description: Plan-review backlog auditing + parallel cross-provider reviews + drift reconciliation is high-throughput repeatable workflow
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orchestration, cross-provider-reviews, plan-governance]
---

Sessions established pattern: query GitHub labels → identify missing Codex/Gemini reviews → run reviews in parallel → post artifacts + GitHub comments → reconcile label/README/local-marker drift → iterate on MAJOR verdicts. 12+ issues reviewed in single wave; non-overlapping provider defects justify parallel execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
