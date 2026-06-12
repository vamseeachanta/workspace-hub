---
name: crossprovider codex test-language-must-directly-falsify-acceptance-c
description: Test language must directly falsify acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, acceptance-alignment, test-specificity]
---

Acceptance criteria stating "every seed record has A, B, C, D, E" require tests checking all five fields for all records. If the test accepts "at least one of these fields", the test is not falsifying the acceptance claim.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
