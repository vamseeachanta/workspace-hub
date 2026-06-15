---
name: crossprovider codex plan-contracts-must-specify-cli-flags-fixture-sc
description: Plan contracts must specify CLI flags, fixture schema, and output paths before plan-review
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, governance, specification]
---

Vague CLI contracts and fixture definitions in plans lead to implementation drift and enable hard-coded assumptions. CLI flags must be fully specified with exact syntax, expected input schema, output paths, fixture sources, and generic vs. canary behavior before the plan can move to status:plan-review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
