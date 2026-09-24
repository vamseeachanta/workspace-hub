---
name: crossprovider codex status-derivation-logic-must-be-enforced-at-vali
description: Status derivation logic must be enforced at validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, state-machines, consistency]
---

When a separate function derives allowed status from combinations of other fields, the validator must check that final status matches the derivation, not just membership in an allowed set. Prevents inconsistent state (e.g., `access_mode=public` but `status=blocked`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
