---
name: crossprovider codex test-harnesses-that-extract-call-paths-create-fa
description: Test harnesses that extract call paths create false-green coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [testing, regression, security-boundaries]
---

A factory harness that extracts only the render/finalize block, pre-seeds derived variables, and uses fake `uv` can pass assertions while missing actual failure modes in clone-config handling, ordering, and error propagation. Harnesses must exercise the full real call chain, not just extracted portions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
