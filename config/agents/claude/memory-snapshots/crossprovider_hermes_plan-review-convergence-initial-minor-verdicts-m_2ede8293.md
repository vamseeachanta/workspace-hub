---
name: crossprovider hermes plan-review-convergence-initial-minor-verdicts-m
description: Plan review convergence: initial MINOR verdicts mask deeper MAJOR authority defects
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-gates, infrastructure-authority, plan-convergence]
---

Infrastructure plan reviews often identify TDD/fixture gaps in first pass (MINOR verdict) that obscure fundamental authority reconciliation failures discovered in follow-up reviews (MAJOR). For path/storage authority plans, verify explicit scope coverage of workspace_root ↔ storage.local ↔ data_access_profile.storage_roots alignment; don't accept MINOR without confirming root reconciliation is load-bearing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
