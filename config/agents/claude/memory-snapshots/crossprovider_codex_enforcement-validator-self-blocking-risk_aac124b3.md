---
name: crossprovider codex enforcement-validator-self-blocking-risk
description: Enforcement/validator self-blocking risk
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [enforcement, self-blocking, test-coverage]
---

When writing validators that enforce standards, the validator itself and test fixtures can trigger the enforcement rules. Explicit tests required proving: (1) validator + legal scan pass on the created standards/templates, (2) invalid fixtures are allowed only under sentinel-scoped paths (fixture/ directories with schema-level exceptions). Prevents enforcement from blocking its own rollout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
