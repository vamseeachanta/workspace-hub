---
name: crossprovider codex symlink-based-test-isolation-is-permeable-to-byt
description: Symlink-based test isolation is permeable to bytecode writes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [test-isolation, python-bytecode, ci-correctness]
---

Symlink isolation in shadow directories does not prevent Python from writing __pycache__ into the real working tree. This violates the claim of read-only verification and can mutate the checkout during test runs, especially problematic in CI where reproducibility matters.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
