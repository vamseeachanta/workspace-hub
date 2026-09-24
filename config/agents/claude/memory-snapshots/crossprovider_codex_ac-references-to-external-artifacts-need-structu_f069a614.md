---
name: crossprovider codex ac-references-to-external-artifacts-need-structu
description: AC references to external artifacts need structural tests that verify the artifacts exist
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, tdd, structural-testing]
---

ACs that require issue references or enforcement rules (e.g., "runbook must reference #2546, #2401, #2550" or "no inline commenter names") need tests that check for their presence/absence. Omitting structural tests lets an implementation satisfy the test suite while missing the AC.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
