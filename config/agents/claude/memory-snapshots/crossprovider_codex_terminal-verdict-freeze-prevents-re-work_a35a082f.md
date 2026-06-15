---
name: crossprovider codex terminal-verdict-freeze-prevents-re-work
description: Terminal verdict freeze prevents re-work
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [verification-flow, state-machine, idempotency]
---

Once a row receives a terminal verdict (verified/rejected), freeze it permanently and exclude from re-selection. Prevents infinite re-review loops and marks decision boundaries explicitly in parse_status.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
