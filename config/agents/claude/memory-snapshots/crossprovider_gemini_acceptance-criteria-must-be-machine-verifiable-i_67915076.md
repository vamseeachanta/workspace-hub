---
name: crossprovider gemini acceptance-criteria-must-be-machine-verifiable-i
description: Acceptance criteria must be machine-verifiable in CI/CD
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [acceptance-criteria, automation, test-strategy]
---

OR clauses with narrative escapes ("PASS OR documented explanation of why not") break automation. All criteria must reduce to numeric thresholds, strict schema validation, or fully machine-parseable formats. Subjective acceptance always fails CI gates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
