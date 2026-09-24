---
name: crossprovider codex baseline-ratchet-model-required-for-enforcement-
description: Baseline + ratchet model required for enforcement rollout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-patterns, ci-cd-gates, rollout-strategy]
---

Hard-failing on pre-existing violations immediately blocks the repo; sustainable approach establishes baseline, WARNs on known debt, FAILs on new regressions, provides migration path. Every linting/check rollout needs this phased approach or it becomes a deployment blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
