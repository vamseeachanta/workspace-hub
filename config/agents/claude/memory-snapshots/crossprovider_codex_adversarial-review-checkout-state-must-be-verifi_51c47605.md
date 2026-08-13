---
name: crossprovider codex adversarial-review-checkout-state-must-be-verifi
description: Adversarial review checkout state must be verified independently
metadata:
  type: reference
  source: codex
  bridged: 2026-08-12
  tags: [adversarial-review, verification, checkout-state, evidence-separation]
---

When conducting adversarial review, verify the actual checkout state (branch, modified files, working tree state) matches the plan's stated preconditions. Don't assume stated 'clean' state; separate working-tree-dependent measurements from source-file evidence if drift is found.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
