---
name: crossprovider hermes canonical-source-plans-must-reconcile-cross-arti
description: Canonical-source plans must reconcile cross-artifact divergence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-gate, data-integrity, defect-class]
---

When a plan treats X as authoritative but repo has competing X-audit, X-registry, X-ledger with conflicting counts (e.g., audit says 425 standards but ledger says 436), the plan is underspecified. Plans claiming canonical metrics must reconcile actual data drift and name the winner before approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
