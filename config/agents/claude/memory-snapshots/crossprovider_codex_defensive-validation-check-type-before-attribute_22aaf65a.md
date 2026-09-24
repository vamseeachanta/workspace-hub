---
name: crossprovider codex defensive-validation-check-type-before-attribute
description: Defensive validation: check type before attribute access
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, error-handling, input-safety]
---

When validating references to external artifacts or user input, validate the object type BEFORE calling methods like `.get()` or accessing attributes. If validation skips the type check, non-object inputs (arrays, strings) crash with `AttributeError` instead of returning an error list. Always validate structure (object/dict/list) before dereferencing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
