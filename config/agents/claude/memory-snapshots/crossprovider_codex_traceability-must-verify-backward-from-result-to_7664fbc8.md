---
name: crossprovider codex traceability-must-verify-backward-from-result-to
description: Traceability must verify backward from result to source row
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [data-integrity, testing, sourcing]
---

Silent data leaks occur when results contain unverified cross-references (e.g., award amounts in narrative links, citations not resolved to live rows). Tests must programmatically resolve each reference back to its authoritative source table and reject unresolved or monetized narratives.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
