---
name: crossprovider codex unknown-solver-evidence-incorrectly-satisfies-ab
description: Unknown solver evidence incorrectly satisfies absent baseline
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [grading, logic-bug, testing]
---

In grading logic, unknown/None evidence for an absent baseline incorrectly returns CONFORMS instead of MISSING-EVIDENCE. Treat unknown/None as MISSING-EVIDENCE for any baseline unless concrete miss dominates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
