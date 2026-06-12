---
name: crossprovider hermes documented-design-limitations-prevent-over-engin
description: Documented design limitations prevent over-engineering
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, design, philosophy]
---

When review finds a limitation (e.g., non-anchored path rewriting), prefer documenting it in tests and comments over redesign. Explicit coverage of limitations signals intentional scope, not bugs, to future maintainers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
