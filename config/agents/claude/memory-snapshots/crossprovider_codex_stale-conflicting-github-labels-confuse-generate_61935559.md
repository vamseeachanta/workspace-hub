---
name: crossprovider codex stale-conflicting-github-labels-confuse-generate
description: Stale/conflicting GitHub labels confuse generated state machines
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [state-machines, generated-output, coordination, github-labels]
---

Generated outputs that read GitHub labels (e.g., status:plan-review AND status:plan-approved together) may encode ambiguous state-machine precedence bugs. Label hygiene is critical for generated-output correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
