---
name: crossprovider codex manifest-routing-claims-need-artifact-verificati
description: Manifest routing claims need artifact verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [manifest-routing, testing, governance]
---

When verifying routing decisions, check that claimed 'existing coverage' references actually exist in the repo. Tests should validate against the approved governance model, not just current manifest structure—fixture-only validation can hide coverage gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
