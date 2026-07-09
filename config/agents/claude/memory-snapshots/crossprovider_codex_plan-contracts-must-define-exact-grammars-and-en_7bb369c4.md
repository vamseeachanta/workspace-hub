---
name: crossprovider codex plan-contracts-must-define-exact-grammars-and-en
description: Plan contracts must define exact grammars and enums upfront
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [planning, contracts, tdd, specification]
---

Plans that defer contract definition to implementation time ("grammar will be defined during implementation") lack sufficient specificity for TDD or test-first approaches. Require normative tables with exact sentinel values, token-class enums, context IDs, heading anchors, and block-malformation rules before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
