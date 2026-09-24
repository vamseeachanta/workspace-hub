---
name: crossprovider codex validator-delegation-requires-explicit-verificat
description: Validator delegation requires explicit verification in adversarial review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator, code-review, testing, contracts]
---

When a validator delegates to upstream contracts (e.g., sampling firewall, metric validation), adversarial testing must verify the delegation actually happens on all code paths, not just that the function is imported. Import presence + passing tests do not prove the delegation is used; probe edge cases where delegation should trigger but doesn't.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
