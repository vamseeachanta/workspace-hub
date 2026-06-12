---
name: crossprovider gemini frozen-dataclass-with-post-init-validation
description: Frozen dataclass with __post_init__ validation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pattern, python, validation]
---

Use `@dataclass(frozen=True)` with `__post_init__` for immutable, self-validating config objects. Seen in ScaleDimensions, RaoReference, CasingString: validates dimensions positive, draft/headings in range, raises ValueError if invalid. Prevents invalid state at construction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
