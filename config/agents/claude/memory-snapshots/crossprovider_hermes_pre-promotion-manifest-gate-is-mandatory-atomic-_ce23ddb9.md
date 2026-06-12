---
name: crossprovider hermes pre-promotion-manifest-gate-is-mandatory-atomic-
description: Pre-promotion manifest gate is mandatory; atomic swap alone is insufficient
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [publication, safety, gates]
---

Atomic publication promotion (#2177 staged swap) cannot prevent manifest divergence or policy violation; a pre-promotion gate (#2178) must validate staged bundle against required-files/forbidden-drift/checksum policies before the atomic swap, not after.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
