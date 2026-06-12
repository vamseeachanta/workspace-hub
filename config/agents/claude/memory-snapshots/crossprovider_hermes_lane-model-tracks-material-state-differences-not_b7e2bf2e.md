---
name: crossprovider hermes lane-model-tracks-material-state-differences-not
description: Lane model tracks material state differences, not just readiness grades
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [throughput-model, execution-tracking, lane-semantics]
---

A single 'approved' or 'ready' bucket collapses fundamentally different states: planned-but-not-approved, approved-but-not-dispatched, dispatched-currently-executing, execution-complete-awaiting-review, and review-blocked-needs-rework. Use explicit lanes (A=approved, B=executable, D=executing, E=review-queue) to prevent invisible active work and false underfill signals.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
