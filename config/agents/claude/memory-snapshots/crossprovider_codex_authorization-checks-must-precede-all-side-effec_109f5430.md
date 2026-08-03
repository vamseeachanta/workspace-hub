---
name: crossprovider codex authorization-checks-must-precede-all-side-effec
description: Authorization checks must precede all side effects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [security, authorization, ordering]
---

Render authorization must happen before scaffold bytes are written. If authorization is deferred until after manifest persistence, forbidden configs or unauthorized origins can still reach file creation. Place security gates before any writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
