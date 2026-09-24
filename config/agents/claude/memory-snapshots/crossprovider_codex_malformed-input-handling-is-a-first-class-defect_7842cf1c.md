---
name: crossprovider codex malformed-input-handling-is-a-first-class-defect
description: Malformed input handling is a first-class defect class, not an edge case
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, testing, validator]
---

Validators receiving non-object JSON or missing required types should return structured errors (enum rejection), not crash with unhandled tracebacks. This defect class is often discovered late in adversarial testing but should be part of initial test design.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
