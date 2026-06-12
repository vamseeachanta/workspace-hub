---
name: crossprovider hermes entry-condition-and-mode-decision-as-explicit-op
description: Entry condition and mode decision as explicit operational gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [execution, gating, operational-discipline, early-validation]
---

Strengthen early execution stages with hard gates: entry condition (approval/authz/readiness checks with clear stop/continue routing), already-done pre-check (verification-first with evidence requirements), and mode selection (central-vs-delegated with evidence requirements and GitHub check-in posting). Only proceed to code changes after all three gates pass. Each gate should post GitHub outcomes explicitly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
