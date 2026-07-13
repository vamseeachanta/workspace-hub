---
name: crossprovider codex owner-decision-required-is-a-valid-terminal-stat
description: Owner-decision-required is a valid terminal state, not a failure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [decision-logic, scoring, landman]
---

When all candidates fail scoring criteria, emit owner_decision_required rather than fabricating a winner. This is correct behavior when evidence legitimately yields no eligible option.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
