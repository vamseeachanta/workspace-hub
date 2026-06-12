---
name: crossprovider gemini stratify-optional-inputs-by-role-in-analysis-too
description: Stratify optional inputs by role in analysis tools
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [tool-design, data-contracts, graceful-degradation]
---

Distinguish reporting-only optional inputs (safe to skip, no completeness impact) from coverage-bearing optional inputs (if configured/expected, absence triggers degraded-run status not crash). Separate degradation semantics prevent false-positive acceptance-gate failures and clarify when partial results are acceptable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
