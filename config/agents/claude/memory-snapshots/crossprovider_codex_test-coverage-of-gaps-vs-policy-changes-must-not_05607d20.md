---
name: crossprovider codex test-coverage-of-gaps-vs-policy-changes-must-not
description: Test coverage of gaps vs policy changes must not be conflated
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [test-design, coverage-gaps, policy]
---

Pinning stale gap expectations in tests while changing acceptance policy hides design disagreement as implementation defects. Tests must explicitly distinguish: which fields are used/defaulted/missing, and why (source class, not just coverage). Coverage claims must be testable and separate from behavior assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
