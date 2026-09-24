---
name: crossprovider codex ioobject-serialization-includes-time-relative-me
description: IOobject serialization includes time-relative metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [physics-simulation, openfoam, verification]
---

OpenFOAM IOobject headers embed location fields relative to time, so identical coordinate meshes hash differently when read at different timesteps. Hash equality cannot prove mesh motion or geometric changes; compare coordinate arrays directly or use deterministic coordinate serialization independent of time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
