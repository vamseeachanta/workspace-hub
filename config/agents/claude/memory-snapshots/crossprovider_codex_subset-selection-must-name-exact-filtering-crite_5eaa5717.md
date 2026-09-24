---
name: crossprovider codex subset-selection-must-name-exact-filtering-crite
description: Subset selection must name exact filtering criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-contracts, specifications, testing]
---

When a plan uses rows from an input manifest but only a subset, explicitly name the filtering criteria (e.g., `candidate_class == 'pre-ai-baseline-archive'`), verify the subset count, and encode that filter in tests. Bare statements like 'only pre-AI rows' allow off-by-one errors when inputs change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
