---
name: crossprovider codex vertical-red-green-order-in-tdd-amendments-block
description: Vertical RED→GREEN order in TDD amendments blocks backtracking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, amendment, test-sequencing]
---

When a plan amendment requires multiple test fixes, list them in execution order with specific test names and parameterization. This lets the implementer work top-to-bottom without discovering mid-implementation that an earlier test's GREEN depends on a later test's fix. Makes amendment auditable and reproducible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
