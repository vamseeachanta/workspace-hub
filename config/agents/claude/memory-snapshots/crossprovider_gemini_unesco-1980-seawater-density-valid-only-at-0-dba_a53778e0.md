---
name: crossprovider gemini unesco-1980-seawater-density-valid-only-at-0-dba
description: UNESCO 1980 seawater density valid only at 0 dbar (surface pressure)
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [seawater-density, boundary-condition, subsea]
---

Simplified 9-coefficient form (0-40°C, 0-42 ppt) assumes 0 dbar. Beyond this boundary, higher-order terms in full UNESCO standard are required. Using at depth causes silent errors. Explicitly document pressure boundary in subsea hydrodynamic code.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
