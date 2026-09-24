---
name: crossprovider codex cross-repo-harness-needs-explicit-policy-for-mis
description: Cross-repo harness needs explicit policy for missing/dirty repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-repo, error-handling, state-assumptions]
---

Implicit assumptions about repo availability, branch state, or cleanliness create brittle behavior. Define explicit policy: fail hard, skip with warning, or require prepared workspace. Document which repo states are supported vs. unsupported.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
