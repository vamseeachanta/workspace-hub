---
name: crossprovider codex contract-definition-resolves-review-stalls
description: Contract definition resolves review stalls
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [contracts, data-definitions, review-gate]
---

Plans stall when they don't define: identity-join rules (bare hex → canonical form handling), output record shapes, failure degradation modes, deletion/purge semantics, duplicate-key handling. Explicit contracts (written as tables, pseudocode, or section headers) resolve these correctness debates and unblock reviewers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
