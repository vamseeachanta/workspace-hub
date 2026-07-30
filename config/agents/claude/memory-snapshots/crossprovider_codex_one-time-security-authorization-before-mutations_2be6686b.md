---
name: crossprovider codex one-time-security-authorization-before-mutations
description: One-time security authorization before mutations doesn't catch concurrent violations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [security, concurrency, authorization]
---

Checking forbidden Git surfaces (alternates, hooks, replace refs, shallow state) once before finalizer operations doesn't protect against concurrent mutations or re-checks during attestation. Security boundaries that guard mutable state must be continuously validated, not just once.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
