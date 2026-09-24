---
name: crossprovider codex hard-coded-issue-selectors-create-generalization
description: Hard-coded issue selectors create generalization debt across multiple surfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture-debt, generalization-risk, multi-surface-updates]
---

When a validator or contract hard-codes a specific issue number (e.g., `issue-68`), generalization issues that expand that logic must update not just the rules file but also config JSON, test module ownership, and CI wiring. Omitting any surface leads to silent failures or self-blocking validators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
