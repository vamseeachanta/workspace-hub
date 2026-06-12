---
name: crossprovider gemini file-taxonomy-explicit-rules-unblock-parallel-mu
description: File taxonomy: explicit rules unblock parallel multi-agent work
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture, file-organization, parallel-work, documentation]
---

Define output directory taxonomy upfront: reports/*.html (human), results/*.npy (machine), data/* (tracked), cache/* (gitignored), specs/wrk/WRK-NNN/ (execution specs). Include naming conventions and gitignore policy in the same reference. Ambiguity about artifact location becomes a bottleneck when parallel agents write outputs — clarity here eliminates friction.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
