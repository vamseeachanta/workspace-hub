---
name: crossprovider codex fake-boundary-hazard-in-test-fixtures
description: Fake boundary hazard in test fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, mocks, boundaries]
---

Synthetic mocks/fakes (e.g., a fake `uv.cmd` in Windows tests) satisfy proof surface without exercising the real boundary they validate. Negative-control tests must use real implementations or explicitly verify that fake and real behaviors diverge on the tested condition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
