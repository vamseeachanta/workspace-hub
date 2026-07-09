---
name: crossprovider codex stale-gate-language-in-unchanged-docs-creates-ap
description: Stale gate language in unchanged docs creates approval coherence defects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [documentation, coherence, approval-gate]
---

When code is fixed (e.g., exact artifact-set validation) but one copy of the approval language remains unchanged (e.g., 'deferred until approval'), that stale wording becomes canonical until updated. Update ALL related docs/plans/evals/CI gates in the same PR; check for phrase-level conflicts like pre-implementation vs. exact-artifact-set language.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
