---
name: crossprovider codex hard-lifecycle-gates-block-implementation-before
description: Hard lifecycle gates block implementation before plan-approved
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, lifecycle-gates, implementation-authorization]
---

Multiple repositories enforce status:plan-approved labels and require explicit user approval before implementation is allowed. The Codex agent respects this boundary and falls back to read-only planning/review work when the gate is not satisfied. Attempting work in an unapproved state will be rejected by governance checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
