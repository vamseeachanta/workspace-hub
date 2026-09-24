---
name: crossprovider codex sparse-checkout-test-suite-fallback-strategy
description: Sparse checkout test suite fallback strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, sparse-checkout, validation]
---

When sparse clones lack sibling imports/modules, full test suite collection fails. Solution: run targeted pytest files for the touched area + syntax checks + CLI smoke runs, skip the full suite. Document the sparse-checkout limitation in the issue comment to set expectations on validation breadth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
