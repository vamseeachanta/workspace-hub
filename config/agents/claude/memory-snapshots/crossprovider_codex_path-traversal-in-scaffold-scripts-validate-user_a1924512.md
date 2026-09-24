---
name: crossprovider codex path-traversal-in-scaffold-scripts-validate-user
description: Path traversal in scaffold scripts: validate user input before interpolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, scaffolding, input-validation]
---

Scaffold scripts accepting formatted identifiers (WRK IDs, resource names) must validate format before path interpolation. Unvalidated input like '../' can write outside the intended tree. Enforce format validation (e.g., `^WRK-[0-9]+$`) before any path operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
