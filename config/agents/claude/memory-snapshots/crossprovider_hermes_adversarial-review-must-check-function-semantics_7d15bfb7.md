---
name: crossprovider hermes adversarial-review-must-check-function-semantics
description: Adversarial review must check function semantics vs. test assertions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, semantics, test-gap]
---

Documentation stated warnings are non-dispatchable; code returned `dispatchable=True` for warn status; tests proved neither the doc claim nor the code behavior. Test-pass alone doesn't verify semantic correctness. Review checklist: (1) read function docstring, (2) read code contract, (3) inspect test assertions, (4) flag mismatches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
