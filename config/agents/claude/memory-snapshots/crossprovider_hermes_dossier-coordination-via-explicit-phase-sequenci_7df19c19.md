---
name: crossprovider hermes dossier-coordination-via-explicit-phase-sequenci
description: Dossier coordination via explicit phase sequencing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-phase-coordination, dossier-orchestration, async-dependencies]
---

Governance Phase 2 (runtime enforcement) must run before Phase 3 (session-start skills) because Phase 3 is documented not to modify Phase 2 artifacts and should wait for hook/env defaults to settle. Pattern: multi-phase work is coordinated not by implicit ordering but by explicit sequencing constraints documented in dossier bodies.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
