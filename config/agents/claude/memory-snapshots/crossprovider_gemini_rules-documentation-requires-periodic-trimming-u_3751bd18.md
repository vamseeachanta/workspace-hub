---
name: crossprovider gemini rules-documentation-requires-periodic-trimming-u
description: Rules documentation requires periodic trimming under context budget constraints
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [documentation, context-budgeting, maintenance]
---

As rules/ files grow, they consume context window tokens. Establish a soft target (e.g., 16KB) and trim aggressively when approached: condense examples, remove redundant sections, use terse language. This is a recurring maintenance task, not one-time.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
