---
name: crossprovider codex scope-boundary-assertions-must-be-attested
description: Scope boundary assertions must be attested
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, scope-boundaries, verification, codex-adversarial]
---

When plans use external issues to justify scope boundaries (e.g., 'this is out of scope per issue #X'), must provide attested evidence the issues exist and have the claimed scope—cannot rely on unverified assertions. Attach verified command output (e.g., `gh issue view` results) when external issues are approval-critical.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
