---
name: crossprovider codex regulatory-exclusions-create-hard-scope-boundari
description: Regulatory exclusions create hard scope boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [regulatory-authority, data-validation]
---

When a regulation explicitly excludes a category (e.g., 33 CFR 143.120 excludes production systems), encode it as a row field and verify in tests. Omitting exclusion checks causes the matrix to overclaim regulatory authority over excluded scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
