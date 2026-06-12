---
name: crossprovider hermes subagent-read-only-constraint-affects-work-distr
description: Subagent read-only constraint affects work distribution for multi-repo tasks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [subagents, sandbox-limits, parallelization]
---

Subagents cannot perform writes, commits, pushes, issue comments, or PRs due to sandbox limits. Multi-repo parallel work must partition as: subagents = recon/analysis/synthesis (read-only), main session = all writes/tests/commits/pushes. Affects task decomposition strategy for tier-1 repo waves.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
