---
name: crossprovider hermes legacy-stub-contracts-must-preserve-caller-side-
description: Legacy stub contracts must preserve caller side effects
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [legacy-compatibility, backward-compat, stub-design]
---

When wrapping stale code with a compatibility stub, maintain side effects expected by live callers. Example: generate-index.py stub still rebuilds INDEX.md if local queue exists, even though the canonical flow moved elsewhere.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
