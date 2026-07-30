---
name: crossprovider codex descriptor-bound-verification-must-reverify-befo
description: Descriptor-bound verification must reverify before mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, lifecycle, verification]
---

If you verify a resource is correctly bound (e.g., git clone is the right target), you must reverify that binding before operations that could swap it (commit, push), not just at verification start. The interval between initial verification and final mutation is an attack surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
