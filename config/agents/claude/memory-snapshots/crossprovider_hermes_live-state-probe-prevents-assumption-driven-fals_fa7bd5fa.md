---
name: crossprovider hermes live-state-probe-prevents-assumption-driven-fals
description: Live-state probe prevents assumption-driven false closure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [verification, state-mismatch, planning-rigor]
---

When user specifies cleanup/state assumptions (e.g., 'cleaned except workspace-hub'), probe live filesystem before planning or committing. Discrepancies (sibling repos still present) are planning signals, not user errors; update plan to reflect reality.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
