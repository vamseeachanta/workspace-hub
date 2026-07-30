---
name: crossprovider codex validate-close-replace-pattern-has-unavoidable-t
description: Validate-close-replace pattern has unavoidable TOCTOU race
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [file-operations, toctou-safety, atomicity, race-conditions]
---

Validating a placeholder file by descriptor, closing it, then replacing by pathname (`os.replace()`) opens a race window where a concurrent replacement can succeed between closure and your replace call. Use exclusive creation (hard-link CAS) or retained identity checks instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
