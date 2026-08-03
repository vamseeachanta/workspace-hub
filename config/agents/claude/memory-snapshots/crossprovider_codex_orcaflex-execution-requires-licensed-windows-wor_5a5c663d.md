---
name: crossprovider codex orcaflex-execution-requires-licensed-windows-wor
description: OrcaFlex execution requires licensed Windows worker on this Linux host
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [orcaflex, licensing, windows-worker, environment-constraint]
---

Real OrcaFlex solver runs cannot execute on Linux hosts lacking OrcFxAPI. Route case bundles to licensed Windows worker via spec.yml→model→statics/dynamics→results pipeline; bring only de-identified inputs and results back for verification and publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
