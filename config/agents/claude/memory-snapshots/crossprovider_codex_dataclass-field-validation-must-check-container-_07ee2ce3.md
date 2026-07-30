---
name: crossprovider codex dataclass-field-validation-must-check-container-
description: Dataclass field validation must check container type, not just elements
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [python, dataclass, validation, schema]
---

Validators that iterate over a field (e.g., `for url in field`) will accept a scalar string for a supposed tuple, processing it character-by-character. Require explicit container-type checks (e.g., `isinstance(field, tuple)`) before assuming structure or iterating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
