---
name: crossprovider codex sparse-checkout-silently-stops-test-collection-b
description: Sparse-checkout silently stops test collection before pytest runs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [testing, git, infrastructure, gotcha]
---

Full-suite test runs can silently fail collection if tracked files are excluded from sparse checkout. Tests never execute, but failure is invisible. Local acceptance passing does not guarantee full-suite coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
