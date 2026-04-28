---
title: "Suction pile preliminary sizing with API p-y/t-z curves"
tags: [suction-pile, api-rp-2a, p-y-curves, t-z-curves, geotechnical, offshore-foundations]
sources:
  - ../sources/elements-suction-pile-sizing-deep-extraction.md
  - /mnt/ace/digitalmodel/references/suction-pile-sizing/SUCTION PILE SIZING PROGRAM.pdf
added: 2026-04-28
last_updated: 2026-04-28
domain: marine-engineering
---

# Suction pile preliminary sizing with API p-y/t-z curves

The Elements suction pile program documents a preliminary sizing method for suction piles where the pile is treated as a rigid body rotating in deforming layered soil.

## Method pattern

1. Define pile geometry, embedment, load elevation, horizontal/vertical loads, and optional moment.
2. Segment embedded length and evaluate local soil properties at segment centers.
3. Compute lateral soil resistance with API RP-2A `p-y` relationships for sand/clay.
4. Compute vertical resistance with API RP-2A `t-z` relationships for sand/clay.
5. Solve rigid-body rotation/pivot by minimizing force and moment residuals with Newton iteration.
6. Report pivot point, tilt angle, and pull-out factor of safety.

## Practical assumptions

- Preliminary sizing can ignore local shell deformation from load-introduction details; detail design still needs local shell/stiffener checks.
- Cyclic loading assumptions provide conservatism when the actual case is static.
- Soil layers are represented as zones and may be limited by available geotechnical data resolution.
- A pull-out factor of safety above 2 is cited as acceptable in the source note, but project criteria should govern.

## Reuse in digitalmodel

A future code-port should separate:

- soil model / API curve generation,
- pile geometry and load case schema,
- nonlinear solve loop,
- verification fixtures from the source PDF appendix,
- wall/local check calculations.

## Cross-links

- Source extraction: [Deep extraction — Elements suction pile sizing corpus](../sources/elements-suction-pile-sizing-deep-extraction.md)
- Related engineering concept: [Pile Capacity — Alpha Method](../../../engineering/wiki/concepts/pile-capacity-alpha-method.md)
