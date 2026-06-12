---
name: crossprovider hermes validation-gate-sequence-before-issue-closure
description: Validation gate sequence before issue closure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, review, github-issues]
---

Before closing an issue: (1) run full test suite, (2) run legal/compliance scan, (3) run adversarial review (multi-provider if available), (4) address all MAJOR findings, (5) commit/push only if reviews pass, (6) then comment and close. Skipping adversarial review before user approval is a known defect.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
