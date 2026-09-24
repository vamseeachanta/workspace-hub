---
name: crossprovider codex coverage-checks-on-count-alone-do-not-guarantee-
description: Coverage checks on count alone do not guarantee correct selection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [input-validation, acceptance-criteria, test-coverage]
---

Checking `len(inputs) == 6` does not verify the six items are the exact set {532,533,534,535,536,537}. Duplicates pass count checks; tests that only assert count will accept wrong items. Always validate exact membership, uniqueness, and identity—and test both the happy path (correct items) and the failure mode (duplicates, wrong items).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
