---
name: crossprovider codex consume-closed-issue-contracts-exactly-don-t-red
description: Consume closed-issue contracts exactly, don't redefine terms
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [contracts, vocabulary, reusability]
---

When a downstream issue (#52) depends on a closed contract (#65), use the same vocabulary (routes: public_llm_wiki, private_sidecar, metadata_only, excluded_no_ingest). Session 4 found no wave-1-specific fixtures existed; reuse the existing schema rather than inventing parallel route/field names.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
