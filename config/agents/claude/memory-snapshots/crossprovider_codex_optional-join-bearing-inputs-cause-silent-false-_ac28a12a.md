---
name: crossprovider codex optional-join-bearing-inputs-cause-silent-false-
description: Optional join-bearing inputs cause silent false negatives
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-contracts, correctness-defect, optional-inputs]
---

If an input marked 'optional (degrade if missing)' is actually used for joins or coverage enumeration, treating it as skip-on-absence creates silent false negatives: missing join corpus silently shrinks reported results. Classify such inputs as fail-closed or emit degraded-run status; never treat as reporting-only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
