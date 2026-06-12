---
name: crossprovider gemini ittc-2011-seawater-viscosity-polynomial-linear-s
description: ITTC 2011 seawater viscosity: polynomial + linear salinity correction
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [seawater-properties, ittc-2011, viscosity]
---

Pure water μ_w = 4.2844e-5 + 1/(0.157*(T+64.993)²-91.296) [Pa·s], valid 0-40°C. Salinity correction: μ_sw = μ_w * (1 + 0.001270*S), S in ppt. This precision is non-approximable; required for subsea hydrodynamic simulations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
