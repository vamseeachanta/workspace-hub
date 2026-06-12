---
name: crossprovider hermes parallel-orcaflexconverter-implementations-creat
description: Parallel OrcaFlexConverter implementations create code drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [duplication, data-model, refactor]
---

Two independent OrcaFlexConverter classes exist: bemrosetta/converters/to_orcaflex.py (uses DiffractionResults, exports YAML/CSV/Excel) and solvers/orcawave/diffraction/scripts/convert_to_orcaflex.py (uses VesselData, loads from HDF5/CSV/Excel). Different data models and xlsx handling. Merge into single canonical converter.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
