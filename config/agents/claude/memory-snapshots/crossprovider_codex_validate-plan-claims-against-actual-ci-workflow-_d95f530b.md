---
name: crossprovider codex validate-plan-claims-against-actual-ci-workflow-
description: Validate plan claims against actual CI workflow evidence before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-08-08
  tags: [planning, ci-workflow, validation, evidence]
---

A plan may claim certain collection behavior (e.g., 'full sweeps happen only on main/nightly'), but actual workflow evidence (PR gating, touched-domain rules, CI gate behavior) can contradict it. Measure against how the CI actually runs, not plan assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
