---
name: crossprovider codex renderer-hard-coded-special-cases-for-resolved-d
description: Renderer hard-coded special cases for resolved debt become stealth debt
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dead-code, debt-tracking, renderer, test-closure, plan-scope]
---

When issue resolution leaves dead special-case branches in renderers (e.g., hard-coded swallow markers), the branch persists as stealth debt if not explicitly scoped for removal and tested. Plan scope must include dead-code removal and add fail-closed tests that verify the special case is gone after resolution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
