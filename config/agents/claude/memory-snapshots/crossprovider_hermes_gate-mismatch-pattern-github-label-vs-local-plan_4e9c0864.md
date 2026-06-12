---
name: crossprovider hermes gate-mismatch-pattern-github-label-vs-local-plan
description: Gate mismatch pattern: GitHub label vs. local plan status divergence blocks execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-workflow, gate-mismatch, deployment-blocker]
---

When a GitHub issue is labeled `status:plan-approved` but local `docs/plans/` header says `plan-review` and `.planning/plan-approved/` marker is absent, safe dispatch is blocked. Example: #2728/#2729 had live approval label but local plan/marker unresolved. **Why:** label/header/marker must be synchronized; mismatches indicate incomplete approval workflow or human override without artifact update. **How to apply:** before executing any issue, verify GitHub label == local plan frontmatter == local approval-marker presence; fail closed if any diverge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
