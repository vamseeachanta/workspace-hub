---
name: crossprovider codex backend-numeric-contracts-are-not-portable-betwe
description: Backend numeric contracts are not portable between solvers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [multi-backend, contracts, validation]
---

OrcaWave and AQWA represent stiffness, inertia origin, and CoG differently. Do not assume numeric equivalence (e.g., C44 stiffness) across backends without proving native restoration semantics and exported GM/C44 agreement within 1%.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
