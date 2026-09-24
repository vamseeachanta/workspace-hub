---
name: crossprovider codex backward-compatibility-via-automatic-field-migra
description: Backward compatibility via automatic field migration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [backward-compat, refactoring, testing]
---

When refactoring field names or structures, add automatic conversion logic (e.g., pre_checks → pre_exit_hooks) and include a test verifying old and new behavior identically. Ensures existing configs work without manual intervention during deprecation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
