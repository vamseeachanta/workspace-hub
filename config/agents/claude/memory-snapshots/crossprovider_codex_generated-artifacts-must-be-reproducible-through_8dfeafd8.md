---
name: crossprovider codex generated-artifacts-must-be-reproducible-through
description: Generated artifacts must be reproducible through their committed entry point
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing-patterns, reproducibility, automation]
---

Tests injecting hand-built fixtures can pass while the actual CLI/entry point produces different output, hiding reproducibility drift. Regression tests must exercise the real execution path (CLI, main(), committed defaults) not just core functions with synthetic inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
