---
name: crossprovider codex remove-placeholder-patterns-from-production-code
description: Remove placeholder patterns from production code, not just instances
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [refactoring, code-contracts, invariants]
---

When replacing placeholder refs (e.g., 'required-new-source-family-issue') with concrete ones, delete the placeholder options from production enums/allowed lists entirely. Add an invariant test asserting all allowed classes emit either 'not-required' or a concrete ref, preventing placeholder leakage in future batches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
