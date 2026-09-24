---
name: crossprovider codex intermediate-status-vocabulary-must-not-leak-to-
description: Intermediate status vocabulary must not leak to output contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contracts, state-management, output-design]
---

Internal/transient statuses (`route-probing-in-progress`, `content-negotiation-pending`) must be separate from final published vocabulary. Intermediate states in output contracts confuse consumers about what is settled vs provisional. Maintain dual vocabularies: working (internal) and final (output).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
