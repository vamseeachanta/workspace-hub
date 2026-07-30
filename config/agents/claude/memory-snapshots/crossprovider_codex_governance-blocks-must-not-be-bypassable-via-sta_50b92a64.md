---
name: crossprovider codex governance-blocks-must-not-be-bypassable-via-sta
description: Governance blocks must not be bypassable via status checks or byte equality
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [governance, verification, decision-gates]
---

If owner_decision_required is set and no owner choice exists, --check must fail, not silently pass because the output file exists. Governance invariants are load-bearing; verification must affirmatively confirm that blocking conditions are respected, not just that artifacts are present.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
