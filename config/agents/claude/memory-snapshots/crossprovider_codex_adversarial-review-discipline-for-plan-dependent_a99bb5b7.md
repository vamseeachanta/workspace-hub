---
name: crossprovider codex adversarial-review-discipline-for-plan-dependent
description: Adversarial review discipline for plan-dependent issue batches
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, review, dependencies, contract-definition]
---

When multiple issues form a dependency chain, each plan must explicitly gate on prerequisites or nest scope. Speculative API definitions in one plan cannot substitute for merged code; missing dependencies must be stated as blockers, not assumptions. Validate that cited artifacts (e.g., `orcawave_asset_resolver.py`) either exist or are explicitly prerequisite-gated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
