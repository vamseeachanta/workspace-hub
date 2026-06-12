---
name: crossprovider gemini ratchet-thresholds-allow-gradual-decay-boiling-f
description: Ratchet thresholds allow gradual decay ('boiling frog')
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [coverage, testing, threshold-design]
---

Allowing 2% coverage drops per commit enables slow degradation over many commits. Ratchets should enforce 0% or ≤0.1% regression to prevent baseline erosion; if relaxation is needed, explicitly update baseline, don't allow drift (WRK-1067).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
