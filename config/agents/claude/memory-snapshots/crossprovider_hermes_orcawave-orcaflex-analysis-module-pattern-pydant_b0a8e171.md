---
name: crossprovider hermes orcawave-orcaflex-analysis-module-pattern-pydant
description: OrcaWave/OrcaFlex analysis module pattern: Pydantic I/O, numpy arrays, no OrcFxAPI
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [package-architecture, pydantic-patterns, orcawave, orcaflex]
---

Expand reporting-only packages with 7-11 analysis modules: RAO/hydro processing, mooring/riser design, pipelay/installation, weather/environment, code checks, VIV screening, post-processing. All standalone (no OrcFxAPI imports), use Pydantic BaseModel for I/O and numpy for arrays. Include 3+ tests per module.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
