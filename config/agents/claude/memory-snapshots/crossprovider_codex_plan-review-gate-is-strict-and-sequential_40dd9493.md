---
name: crossprovider codex plan-review-gate-is-strict-and-sequential
description: Plan review gate is strict and sequential
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-gate, governance]
---

Workflow is Issue → Plan (draft) → Adversarial review → push plan + review artifacts → add status:plan-review label → user approval (status:plan-approved) → implementation. Never self-apply status:plan-approved; user approval is a load-bearing gate. Add status:plan-review label only after review artifacts are pushed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
