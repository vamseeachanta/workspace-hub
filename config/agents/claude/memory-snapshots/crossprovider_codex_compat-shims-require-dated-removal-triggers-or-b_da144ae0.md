---
name: crossprovider codex compat-shims-require-dated-removal-triggers-or-b
description: Compat shims require dated removal triggers or become permanent debt
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [backwards-compat, tech-debt, infrastructure]
---

Every read-compat map (old token → new token, old schema → new schema) should have an explicit date after which it is removed. Without a dated trigger, the shim becomes invisible tech debt. Codex found no removal date for the read-compat layer in #581, making permanent support the default.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
