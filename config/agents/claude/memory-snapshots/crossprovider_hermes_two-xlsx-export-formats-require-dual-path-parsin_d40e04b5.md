---
name: crossprovider hermes two-xlsx-export-formats-require-dual-path-parsin
description: Two xlsx export formats require dual-path parsing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-format, xlsx, orcawave]
---

OrcaWave exports two xlsx formats: Native (complex multi-sheet from GUI: Panel geometry, Hydrostatics, Haskind loads, etc.) vs Pipeline (simple 5-sheet from process-queue.py: Summary, RAOs, AddedMass, Damping, Discretization). Parsers must handle both. Pipeline format is cleaner; prefer it for new exports.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
