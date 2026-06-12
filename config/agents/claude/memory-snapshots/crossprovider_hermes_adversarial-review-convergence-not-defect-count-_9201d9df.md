---
name: crossprovider hermes adversarial-review-convergence-not-defect-count-
description: Adversarial review convergence (not defect count) is the approval signal
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, plan-review-gate, approval-readiness, quality-signals]
---

The #2443 assessment reveals that approval-readiness is signaled by convergence: plan self-declares ready + latest review artifacts are clean (no MAJOR) + artifacts are committed + GitHub label matches. Divergence between these signals is the red flag (e.g., plan says ready but reviews are MAJOR, or latest reviews are uncommitted/dirty). Individual defect counts are noise; the load-bearing signal is whether plan, reviews, and GitHub state agree on blocking status.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
