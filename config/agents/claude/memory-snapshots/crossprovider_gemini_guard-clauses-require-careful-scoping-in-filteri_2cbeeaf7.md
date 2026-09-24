---
name: crossprovider gemini guard-clauses-require-careful-scoping-in-filteri
description: Guard clauses require careful scoping in filtering logic
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell-logic, filtering, control-flow]
---

Early returns in nested conditionals must be scoped to intended output buckets only. Misplaced guards suppress items from other sections unintentionally. Example: periodic-item skip should apply to pending-buckets only, not working/blocked sections.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
