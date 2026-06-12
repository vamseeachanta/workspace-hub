---
name: crossprovider codex plan-dependency-gates-must-land-or-provide-fallb
description: Plan dependency gates must land or provide fallback for future APIs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-dependencies, multi-issue-scope]
---

Plans that block on future implementations (e.g., `OrcaWaveAssetResolver`, `mesh_preflight.py`) create blockers for downstream issues unless the blocker plan explicitly lands those APIs or provides a fallback implementation path. Gate language like 'blocked until #605 lands' without an implementation fallback is implementable-blocking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
