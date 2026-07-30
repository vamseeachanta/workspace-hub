---
name: crossprovider codex semantics-must-precede-identity-hashing
description: Semantics must precede identity hashing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [identity, semantics, reproducibility]
---

Hashing identities before domain-critical semantics are frozen (e.g., coordinate frames, conventions, rotation rules) creates unstable identities that break reproducibility. Define all semantic rules before committing case/result IDs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
