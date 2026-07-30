---
name: crossprovider codex red-green-cycle-on-major-contract-defects-not-ad
description: RED/GREEN cycle on MAJOR contract defects, not ad-hoc fixes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [tdd, code-review, quality]
---

When adversarial review finds MAJOR contract failures (e.g., incoherent state invariants, fail-open routes), dispatch fresh fix agent with scoped defect set and rerun RED/GREEN from scratch. Ad-hoc patching masks the underlying contract design defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
