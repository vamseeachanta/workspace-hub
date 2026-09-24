---
name: crossprovider codex fallback-and-error-handling-modes-must-be-explic
description: Fallback and error-handling modes must be explicitly specified, not implied by pseudocode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, fallback-design, test-driven-design]
---

Sessions #610 and #613 found that dry-run vs license-failure vs missing-API vs path-invalid all have unclear outcomes (pytest skip vs error_message vs warnings). Write tests first to define expected behavior for each failure mode before writing implementation pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
