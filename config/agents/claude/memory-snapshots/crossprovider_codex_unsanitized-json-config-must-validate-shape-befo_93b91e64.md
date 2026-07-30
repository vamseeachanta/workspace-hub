---
name: crossprovider codex unsanitized-json-config-must-validate-shape-befo
description: Unsanitized JSON config must validate shape before use
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [input-validation, error-handling, fail-closed]
---

Accepting arbitrary JSON as configuration (e.g., provenance object, runtime selector) without shape validation causes AttributeError/TypeError in downstream `.get()` or set() calls. Validate shape upfront (must be dict, not list/null/scalar) with sanitized error messages before database work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
