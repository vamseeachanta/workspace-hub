---
name: crossprovider codex test-first-frozen-test-test-is-design-authority-
description: Test-first + frozen test = test IS design authority; surface contradictions, don't fix tests
metadata:
  type: reference
  source: codex
  bridged: 2026-08-05
  tags: [tdd, testing, design, frozen-spec]
---

When a contract test spec has internal contradictions (e.g., one test requires a field, another test's fixture omits it), identify the contradiction precisely but do not edit the test. The user must approve the correction. Treating the frozen test as the design authority prevents workflow confusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
