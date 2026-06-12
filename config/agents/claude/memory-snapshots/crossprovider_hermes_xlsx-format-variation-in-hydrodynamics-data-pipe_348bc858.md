---
name: crossprovider hermes xlsx-format-variation-in-hydrodynamics-data-pipe
description: XLSX format variation in hydrodynamics data pipelines
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hydrodynamics, xlsx-parsing, orcawave, data-format, quirk]
---

Two XLSX formats coexist: pipeline-processed format (from process-queue.py, cleaner columns) and native solver output (OrcaWave/OrcaFlex, text-marked frequency blocks). Auto-detection via header inspection is needed. Native format uses text rows like 'Added mass for frequency X.X rad/s' to mark blocks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
