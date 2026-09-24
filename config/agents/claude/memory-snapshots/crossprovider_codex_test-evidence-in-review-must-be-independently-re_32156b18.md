---
name: crossprovider codex test-evidence-in-review-must-be-independently-re
description: Test evidence in review must be independently reproducible
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, review-process, evidence-verification, quality-gate]
---

Claimed test results ('8/8 PASS') must execute successfully in the reviewer's environment; actual file state must match the claimed fixes (not just summary statements). When claimed test output and actual codebase state diverge, the evidence is unverifiable and the verdict should not proceed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
