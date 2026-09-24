---
name: crossprovider codex separate-read-only-probes-from-write-authorizati
description: Separate read-only probes from write authorization semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [authorization-design, separation-of-concerns, threat-model]
---

When adding a knowledge-query or data-retrieval layer to an auth/audit system (e.g., Deckhand), design the read-only probe surface separately from write authorization paths, even if both are scope-gated and audited. Do not reuse write-path authorization semantics for reads; they have different threat models and requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
