---
name: crossprovider codex review-artifact-status-contradictions-signal-inc
description: Review-artifact status contradictions signal incomplete planning
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, review-gate, status-consistency]
---

Plans cannot simultaneously list review artifacts in the header (implying they exist) and mark them PENDING in the Adversarial Review Summary. This contradiction violates the hard gate requiring completed reviews before approval. Reconcile artifact status with repo hard-gate requirements before accepting the plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
