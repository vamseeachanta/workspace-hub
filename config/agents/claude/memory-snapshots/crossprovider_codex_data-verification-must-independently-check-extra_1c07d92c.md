---
name: crossprovider codex data-verification-must-independently-check-extra
description: Data verification must independently check extraction fidelity and corresponding prose claims
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [QA, verification, data-validation, documentation]
---

Verifying extracted data (CSVs, JSON) matches source files is necessary but insufficient. False prose claims in documentation (e.g., 'all models use identical values' when only subsets match) hide in data audits. Always verify extracted data fidelity separately from the prose/claims that describe it; re-review can refine nuanced differences.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
