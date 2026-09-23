---
name: crossprovider codex hand-verify-fixture-arithmetic-independently
description: Hand-verify fixture arithmetic independently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [testing, verification, domain-knowledge]
---

When tests encode expected behavior (e.g., corrected_load == 277.21176 lb), independently compute from inputs and cite the derivation in comments. Existing tests can lock in wrong ratios (e.g., helical threshold 2×sqrt(2) vs sqrt(2)).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
