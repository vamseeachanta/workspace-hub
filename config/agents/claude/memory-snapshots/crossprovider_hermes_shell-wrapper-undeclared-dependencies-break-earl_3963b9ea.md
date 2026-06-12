---
name: crossprovider hermes shell-wrapper-undeclared-dependencies-break-earl
description: Shell wrapper undeclared dependencies break early-exit paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-portability, dependency-coupling, docs-impl-mismatch]
---

When docs specify one tool (e.g., python3) but implementation uses another (e.g., uv run python), failure modes in error-generation paths fail outright. Scripts using python3-equivalent operations in error handlers must not introduce tool dependencies beyond those documented in portability baseline.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
