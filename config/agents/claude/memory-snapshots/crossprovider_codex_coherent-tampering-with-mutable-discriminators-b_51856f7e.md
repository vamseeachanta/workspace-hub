---
name: crossprovider codex coherent-tampering-with-mutable-discriminators-b
description: Coherent tampering with mutable discriminators bypasses single-axis validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [security, validation, evidence-integrity]
---

When validation chains check hash integrity, including mutable fields (e.g., path discriminators) that are validated optionally enables coherent tampering: attacker can change output, recalculate all downstream hashes, and downgrade the mutable field to bypass validation. Discriminator fields must be immutable or exhaustively validated; optional validation creates a true security gap.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
