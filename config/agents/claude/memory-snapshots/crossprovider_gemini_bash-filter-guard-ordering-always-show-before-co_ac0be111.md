---
name: crossprovider gemini bash-filter-guard-ordering-always-show-before-co
description: Bash filter guard ordering: always-show before conditional-exclude
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash, control-flow, work-queue]
---

When filtering items by status, order guards so "always show" categories (working, blocked) return early BEFORE "sometimes exclude" logic (periodic items in pending only). Reversed order silently suppresses unintended categories due to early return.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
