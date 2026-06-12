---
name: crossprovider hermes tests-passing-against-placeholders-signal-incomp
description: Tests passing against placeholders signal incomplete coverage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, test-design, placeholder-antipattern]
---

A test checking string presence (e.g., placeholder marker) passes when placeholder exists but fails to validate real behavior. Placeholder + test passing = incomplete implementation. Behavioral tests must exercise actual logic, not just string patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
