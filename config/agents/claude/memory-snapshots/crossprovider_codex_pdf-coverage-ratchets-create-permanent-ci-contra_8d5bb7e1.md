---
name: crossprovider codex pdf-coverage-ratchets-create-permanent-ci-contra
description: PDF coverage ratchets create permanent CI contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [ci-design, ratchet, capabilities]
---

Once pdf_gaps is empty, any future section without a one-pager PDF fails CI permanently. This is a first-class testable contract, not aspirational; future work must respect the ratchet to avoid blocking CI.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
