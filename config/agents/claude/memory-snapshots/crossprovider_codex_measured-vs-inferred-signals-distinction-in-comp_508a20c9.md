---
name: crossprovider codex measured-vs-inferred-signals-distinction-in-comp
description: Measured vs. inferred signals distinction in compliance reporting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-compliance, governance]
---

Only explicit stage signals emitted by scripts/logging count for compliance; inferred signals (heuristic reconstruction from state) are not valid evidence. This prevents false positives in gate verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
