---
name: crossprovider codex reproducible-test-claims-require-exact-command-a
description: Reproducible test claims require exact command and environment
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, testing, plan-rigor]
---

Assertions like "164 passed" without specifying pytest command, Python environment, and import paths are not reproducible. Undeclared fixtures cause collection failures. Always include exact `pytest <path> <args>` invocation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
